"""Defines a mixin for incorporating some logging functionality."""

import os
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType
from typing import Callable, Generic, Self, Sequence, TypeVar

from torch import Tensor

from mlfab.core.conf import Device as BaseDeviceConfig, field
from mlfab.core.state import State
from mlfab.nn.parallel import is_master
from mlfab.task.logger import ChannelSelectMode, Logger, LoggerImpl, Number
from mlfab.task.loggers.json import JsonLogger
from mlfab.task.loggers.state import StateLogger
from mlfab.task.loggers.stdout import StdoutLogger
from mlfab.task.loggers.tensorboard import TensorboardLogger
from mlfab.task.mixins.artifacts import ArtifactsConfig, ArtifactsMixin
from mlfab.utils.text import is_interactive_session


@dataclass(kw_only=True)
class LoggerConfig(ArtifactsConfig):
    device: BaseDeviceConfig = field(BaseDeviceConfig(), help="Device configuration")


Config = TypeVar("Config", bound=LoggerConfig)


def get_env_var(name: str, default: bool) -> bool:
    if name not in os.environ:
        return default
    return os.environ[name].strip() == "1"


class LoggerMixin(ArtifactsMixin[Config], Generic[Config]):
    def __init__(self, config: Config) -> None:
        super().__init__(config)

        self.logger = Logger()

    def log_directory(self) -> Path | None:
        return None

    def add_logger(self, *logger: LoggerImpl) -> None:
        self.logger.add_logger(*logger)

    def set_loggers(self) -> None:
        if is_master():
            self.add_logger(
                StdoutLogger(exp_dir=self.exp_dir) if is_interactive_session() else JsonLogger(exp_dir=self.exp_dir),
                StateLogger(self.exp_dir),
                TensorboardLogger(self.exp_dir),
            )

    def write_logs(self, state: State) -> None:
        self.logger.write(state)

    def log_scalar(self, key: str, value: Callable[[], Number] | Number, *, namespace: str | None = None) -> None:
        self.logger.log_scalar(key, value, namespace=namespace)

    def log_string(self, key: str, value: Callable[[], str] | str, *, namespace: str | None = None) -> None:
        self.logger.log_string(key, value, namespace=namespace)

    def log_image(
        self,
        key: str,
        value: Callable[[], Tensor] | Tensor,
        *,
        namespace: str | None = None,
        keep_resolution: bool = False,
    ) -> None:
        self.logger.log_image(
            key,
            value,
            namespace=namespace,
            keep_resolution=keep_resolution,
        )

    def log_labeled_image(
        self,
        key: str,
        value: Callable[[], tuple[Tensor, str]] | tuple[Tensor, str],
        *,
        namespace: str | None = None,
        max_line_length: int | None = None,
        keep_resolution: bool = False,
        centered: bool = True,
    ) -> None:
        self.logger.log_labeled_image(
            key,
            value,
            namespace=namespace,
            max_line_length=max_line_length,
            keep_resolution=keep_resolution,
            centered=centered,
        )

    def log_images(
        self,
        key: str,
        value: Callable[[], Tensor] | Tensor,
        *,
        namespace: str | None = None,
        keep_resolution: bool = False,
        max_images: int | None = None,
        sep: int = 0,
    ) -> None:
        self.logger.log_images(
            key,
            value,
            namespace=namespace,
            keep_resolution=keep_resolution,
            max_images=max_images,
            sep=sep,
        )

    def log_labeled_images(
        self,
        key: str,
        value: Callable[[], tuple[Tensor, Sequence[str]]] | tuple[Tensor, Sequence[str]],
        *,
        namespace: str | None = None,
        max_line_length: int | None = None,
        keep_resolution: bool = False,
        max_images: int | None = None,
        sep: int = 0,
        centered: bool = True,
    ) -> None:
        self.logger.log_labeled_images(
            key,
            value,
            namespace=namespace,
            max_line_length=max_line_length,
            keep_resolution=keep_resolution,
            max_images=max_images,
            sep=sep,
            centered=centered,
        )

    def log_audio(
        self,
        key: str,
        value: Callable[[], Tensor] | Tensor,
        *,
        namespace: str | None = None,
        sample_rate: int = 44100,
        log_spec: bool = True,
        n_fft_ms: float = 32.0,
        hop_length_ms: float | None = None,
        channel_select_mode: ChannelSelectMode = "first",
        keep_resolution: bool = False,
    ) -> None:
        self.logger.log_audio(
            key,
            value,
            namespace=namespace,
            sample_rate=sample_rate,
            log_spec=log_spec,
            n_fft_ms=n_fft_ms,
            hop_length_ms=hop_length_ms,
            channel_select_mode=channel_select_mode,
            keep_resolution=keep_resolution,
        )

    def log_audios(
        self,
        key: str,
        value: Callable[[], Tensor] | Tensor,
        *,
        namespace: str | None = None,
        sep_ms: float = 0.0,
        max_audios: int | None = None,
        sample_rate: int = 44100,
        log_spec: bool = True,
        n_fft_ms: float = 32.0,
        hop_length_ms: float | None = None,
        channel_select_mode: ChannelSelectMode = "first",
        spec_sep: int = 0,
        keep_resolution: bool = False,
    ) -> None:
        self.logger.log_audios(
            key,
            value,
            namespace=namespace,
            sep_ms=sep_ms,
            max_audios=max_audios,
            sample_rate=sample_rate,
            log_spec=log_spec,
            n_fft_ms=n_fft_ms,
            hop_length_ms=hop_length_ms,
            channel_select_mode=channel_select_mode,
            spec_sep=spec_sep,
            keep_resolution=keep_resolution,
        )

    def log_spectrogram(
        self,
        key: str,
        value: Callable[[], Tensor] | Tensor,
        *,
        namespace: str | None = None,
        sample_rate: int = 44100,
        n_fft_ms: float = 32.0,
        hop_length_ms: float | None = None,
        channel_select_mode: ChannelSelectMode = "first",
        keep_resolution: bool = False,
    ) -> None:
        self.logger.log_spectrogram(
            key,
            value,
            namespace=namespace,
            sample_rate=sample_rate,
            n_fft_ms=n_fft_ms,
            hop_length_ms=hop_length_ms,
            channel_select_mode=channel_select_mode,
            keep_resolution=keep_resolution,
        )

    def log_spectrograms(
        self,
        key: str,
        value: Callable[[], Tensor] | Tensor,
        *,
        namespace: str | None = None,
        max_audios: int | None = None,
        sample_rate: int = 44100,
        n_fft_ms: float = 32.0,
        hop_length_ms: float | None = None,
        channel_select_mode: ChannelSelectMode = "first",
        spec_sep: int = 0,
        keep_resolution: bool = False,
    ) -> None:
        self.logger.log_spectrograms(
            key,
            value,
            namespace=namespace,
            max_audios=max_audios,
            sample_rate=sample_rate,
            n_fft_ms=n_fft_ms,
            hop_length_ms=hop_length_ms,
            channel_select_mode=channel_select_mode,
            spec_sep=spec_sep,
            keep_resolution=keep_resolution,
        )

    def log_video(
        self,
        key: str,
        value: Callable[[], Tensor] | Tensor,
        *,
        namespace: str | None = None,
        fps: int | None = None,
        length: float | None = None,
    ) -> None:
        self.logger.log_video(
            key,
            value,
            namespace=namespace,
            fps=fps,
            length=length,
        )

    def log_videos(
        self,
        key: str,
        value: Callable[[], Tensor | list[Tensor]] | Tensor | list[Tensor],
        *,
        namespace: str | None = None,
        max_videos: int | None = None,
        sep: int = 0,
        fps: int | None = None,
        length: int | None = None,
    ) -> None:
        self.logger.log_videos(
            key,
            value,
            namespace=namespace,
            max_videos=max_videos,
            sep=sep,
            fps=fps,
            length=length,
        )

    def log_histogram(self, key: str, value: Callable[[], Tensor] | Tensor, *, namespace: str | None = None) -> None:
        self.logger.log_histogram(key, value, namespace=namespace)

    def log_point_cloud(
        self,
        key: str,
        value: Callable[[], Tensor] | Tensor,
        *,
        namespace: str | None = None,
        max_points: int = 1000,
        colors: Callable[[], Tensor] | Tensor | None = None,
    ) -> None:
        self.logger.log_point_cloud(
            key,
            value,
            namespace=namespace,
            max_points=max_points,
            colors=colors,
        )

    def __enter__(self) -> Self:
        self.logger.__enter__()
        return self

    def __exit__(self, t: type[BaseException] | None, e: BaseException | None, tr: TracebackType | None) -> None:
        self.logger.__exit__(t, e, tr)
        return super().__exit__(t, e, tr)
