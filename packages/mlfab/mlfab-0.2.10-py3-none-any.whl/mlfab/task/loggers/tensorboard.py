"""Defines a Tensorboard logger backend."""

import atexit
import functools
import logging
import os
import re
import shutil
import subprocess
import threading
import time
from pathlib import Path
from typing import TypeVar

import torch
import torch.distributed
from omegaconf import DictConfig, OmegaConf
from torch.utils.tensorboard import SummaryWriter

from mlfab.core.state import Phase
from mlfab.nn.parallel import is_master, port_is_busy
from mlfab.task.logger import TARGET_FPS, LoggerImpl, LogLine
from mlfab.utils.logging import LOG_STATUS

logger: logging.Logger = logging.getLogger(__name__)

T = TypeVar("T")

WRITE_PROC_TEXT_EVERY_N_SECONDS: int = 60 * 2
DEFAULT_TENSORBOARD_PORT = 9249


class TensorboardLogger(LoggerImpl):
    def __init__(
        self,
        run_directory: str | Path,
        subdirectory: str = "tensorboard",
        flush_seconds: float = 10.0,
        wait_seconds: float = 0.0,
        start_in_subprocess: bool = True,
        use_localhost: bool = False,
        log_interval_seconds: float = 10.0,
    ) -> None:
        """Defines a logger which writes to Tensorboard.

        Args:
            run_directory: The root run directory.
            subdirectory: The subdirectory of the run directory to write
                Tensorboard logs to.
            flush_seconds: How often to flush logs.
            wait_seconds: Time to wait before starting Tensorboard process.
            start_in_subprocess: Start TensorBoard subprocess.
            use_localhost: Use localhost for TensorBoard address.
            log_interval_seconds: The interval between successive log lines.
        """
        super().__init__(log_interval_seconds)

        self.run_directory = Path(run_directory).expanduser().resolve()
        self.log_directory = self.run_directory / subdirectory
        self.flush_seconds = flush_seconds
        self.wait_seconds = wait_seconds
        self.start_in_subprocess = start_in_subprocess
        self.use_localhost = use_localhost

        self.proc: subprocess.Popen | None = None

        self.git_state: str | None = None
        self.training_code: str | None = None
        self.config: DictConfig | None = None
        self.task_info: tuple[str, Path] | None = None

        self._started = False

    def _start(self) -> None:
        if self._started:
            return

        if is_master():
            threading.Thread(target=self.worker_thread, daemon=True).start()

        self._started = True

    def log_task_info(self, task_name: str, task_path: Path) -> None:
        self.task_info = task_name, task_path

    def worker_thread(self) -> None:
        time.sleep(self.wait_seconds)

        port = int(os.environ.get("TENSORBOARD_PORT", DEFAULT_TENSORBOARD_PORT))
        if port < 1:
            logger.warning("Tensorboard is disabled because TENSORBOARD_PORT is not positive")
            return

        while port_is_busy(port):
            logger.warning(f"Port {port} is busy, waiting...")
            time.sleep(10)

        def make_localhost(s: str) -> str:
            if self.use_localhost:
                s = re.sub(rf"://(.+?):{port}", f"://localhost:{port}", s)
            return s

        def parse_url(s: str) -> str:
            m = re.search(r" (http\S+?) ", s)
            if m is None:
                return s
            return f"Tensorboard: {m.group(1)}"

        command: list[str] = [
            "tensorboard",
            "serve",
            "--logdir",
            str(self.log_directory),
            "--bind_all",
            "--port",
            str(port),
            "--reload_interval",
            "15",
        ]

        if not self.start_in_subprocess:
            logger.warning("Tensorboard subprocess disabled because start_in_subprocess=False")

        else:
            self.proc = subprocess.Popen(  # pylint: disable=consider-using-with
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )

            # Gets the output line that shows the running address.
            assert self.proc is not None and self.proc.stdout is not None
            lines = []
            for line in self.proc.stdout:
                line_str = line.decode("utf-8")
                if line_str.startswith("TensorBoard"):
                    line_str = parse_url(make_localhost(line_str))
                    logger.log(LOG_STATUS, line_str)
                    break
                lines.append(line_str)
            else:
                line_str = "".join(lines)
                raise RuntimeError(f"Tensorboard failed to start:\n{line_str}")

            atexit.register(self.cleanup)

    def cleanup(self) -> None:
        if self.proc is not None:
            self.proc.terminate()
            self.proc.wait()
            self.proc = None

    def __del__(self) -> None:
        self.cleanup()

    @functools.cached_property
    def train_writer(self) -> SummaryWriter:
        return SummaryWriter(self.log_directory / "train", flush_secs=self.flush_seconds)

    @functools.cached_property
    def valid_writer(self) -> SummaryWriter:
        return SummaryWriter(self.log_directory / "valid", flush_secs=self.flush_seconds)

    @functools.lru_cache(None)  # Avoid clearing logs multiple times.
    def clear_logs(self) -> None:
        if not self.log_directory.exists():
            return
        if not any(child.is_dir() for child in self.log_directory.iterdir()):
            return
        logger.warning("Clearing TensorBoard logs")
        shutil.rmtree(self.log_directory)

    def get_writer(self, phase: Phase) -> SummaryWriter:
        self._start()
        match phase:
            case "train":
                return self.train_writer
            case "valid":
                return self.valid_writer
            case _:
                raise NotImplementedError(f"Unexpected phase: {phase}")

    def log_git_state(self, git_state: str) -> None:
        if not is_master():
            return
        self.git_state = f"```\n{git_state}\n```"

    def log_training_code(self, training_code: str) -> None:
        if not is_master():
            return
        self.training_code = f"```python\n{training_code}\n```"

    def log_config(self, config: DictConfig) -> None:
        if not is_master():
            return
        self.config = config

    def write(self, line: LogLine) -> None:
        if not is_master():
            return

        if line.state.num_steps == 0:
            self.clear_logs()

        writer = self.get_writer(line.state.phase)
        walltime = line.state.start_time_s + line.state.elapsed_time_s

        for namespace, scalars in line.scalars.items():
            for scalar_key, scalar_value in scalars.items():
                writer.add_scalar(
                    f"{namespace}/{scalar_key}",
                    scalar_value,
                    global_step=line.state.num_steps,
                    walltime=walltime,
                )

        for namespace, strings in line.strings.items():
            for string_key, string_value in strings.items():
                writer.add_text(
                    f"{namespace}/{string_key}",
                    string_value,
                    global_step=line.state.num_steps,
                    walltime=walltime,
                )

        for namespace, images in line.images.items():
            for image_key, image_value in images.items():
                writer.add_image(
                    f"{namespace}/{image_key}",
                    image_value.pixels,
                    global_step=line.state.num_steps,
                    walltime=walltime,
                )

        for namespace, audios in line.audios.items():
            for audio_key, audio_value in audios.items():
                writer.add_audio(
                    f"{namespace}/{audio_key}",
                    audio_value.frames,
                    global_step=line.state.num_steps,
                    walltime=walltime,
                    sample_rate=audio_value.sample_rate,
                )

        for namespace, videos in line.videos.items():
            for video_key, video_value in videos.items():
                writer.add_video(
                    f"{namespace}/{video_key}",
                    video_value.frames.unsqueeze(0),
                    global_step=line.state.num_steps,
                    walltime=walltime,
                    fps=TARGET_FPS,
                )

        for namespace, point_cloud in line.point_cloud.items():
            for pc_key, pc_item in point_cloud.items():
                pc_value, colors = pc_item.xyz, pc_item.colors
                bsz, _, _ = pc_value.shape
                if colors is None:
                    colors = torch.randint(0, 255, (bsz, 1, 3), device=pc_value.device).expand_as(pc_value)
                pc_value, colors = pc_value.flatten(0, 1).unsqueeze(0), colors.flatten(0, 1).unsqueeze(0)
                writer.add_mesh(
                    f"{namespace}/{pc_key}",
                    pc_value,
                    colors=colors,
                    global_step=line.state.num_steps,
                    walltime=walltime,
                )

        if self.config is not None:
            writer.add_text("config", f"```\n{OmegaConf.to_yaml(self.config)}\n```")
            self.config = None

        if self.task_info is not None:
            task_name, task_path = self.task_info
            task_info_string = "\n".join(
                [
                    f"Task: {task_name}",
                    f"Path: {task_path}",
                    f"Experiment directory: {self.run_directory}",
                ]
            )
            writer.add_text("task", task_info_string)
            self.task_info = None

        if self.git_state is not None:
            writer.add_text("git", self.git_state)
            self.git_state = None

        if self.training_code is not None:
            writer.add_text("code", self.training_code)
            self.training_code = None
