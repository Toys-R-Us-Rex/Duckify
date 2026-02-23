from pathlib import Path

import numpy as np
from PIL.Image import Image

from tracing.color import Color
from tracing.island import Island
from tracing.point_3d import Point3D
from tracing.segment import Segment
from tracing.trace import Trace


class Tracer:
    def __init__(self, texture_path: Path, model_path: Path, palette: tuple[Color, ...]):
        self.texture_path: Path = texture_path
        self.model_path: Path = model_path
        self.palette: tuple[Color, ...] = palette

        self.islands: list[Island] = []
        self.segments: list[Segment] = []
        self.traces: list[Trace] = []

    def compute_traces(self) -> list[Trace]:
        return self.traces

    def load_texture(self):
        pass

    def load_model(self):
        pass

    def discretize_texture_colors(self):
        pass

    def split_colors(self, img: Image) -> list[Image]:
        return []

    def detect_islands(self, img: Image) -> list[Island]:
        return []

    def resample_border(self, island: Island) -> list[Segment]:
        return []

    def compute_fill_slices(self, island: Island) -> list[Segment]:
        return []

    def resample_fill_segment(self, segment: Segment) -> list[Segment]:
        return []

    def project_segment_to_3d(self, segment: Segment) -> Trace:
        pass

    def interpolate_position(self, uv_pos: np.ndarray) -> Point3D:
        pass
