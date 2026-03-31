from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from tracing.color import Color
from tracing.config import TracerConfig
from tracing.stats import TracingStats
from tracing.tracer import Tracer

IGNORED_COLOR: Color = (173,170,75) #TODO rendre cela configurable dans l'UI


@dataclass
class TracingRequest:
    model_path: Path
    mask_path: Path
    texture_path: Path
    palette: list[Color]
    enable_fill_slicing: bool


@dataclass
class TracingResult:
    stats: TracingStats
    traces_path: Path
    paletted_texture_path: Optional[Path]


ProgressCallback = Callable[[int, int, str], None]


class TracingService:
    def __init__(self, traces_path: Path, paletted_texture_path: Path) -> None:
        self.traces_path: Path = traces_path
        self.paletted_texture_path: Path = paletted_texture_path

    def run(
        self, request: TracingRequest, on_progress: Optional[ProgressCallback]
    ) -> TracingResult:
        config: TracerConfig = TracerConfig(
            enable_fill_slicing=request.enable_fill_slicing
        )
        tracer: Tracer = Tracer(
            config=config,
            texture_path=request.texture_path,
            model_path=request.model_path,
            mask_path=request.mask_path,
            palette=tuple(request.palette),
            color_not_to_draw = IGNORED_COLOR,
        )

        stats: TracingStats = tracer.compute_traces(progress_callback=on_progress)
        tracer.export_traces(self.traces_path, force=True)

        paletted_path: Optional[Path] = None
        if tracer.paletted_texture is not None:
            tracer.paletted_texture.save(self.paletted_texture_path)
            paletted_path = self.paletted_texture_path

        return TracingResult(
            stats=stats,
            traces_path=self.traces_path,
            paletted_texture_path=paletted_path,
        )
