from pathlib import Path
from typing import Optional

import numpy as np
from PIL.Image import Image
import tqdm

from tracing.color import Color
from tracing.island import Island
from tracing.point_3d import Point3D
from tracing.segment import Segment
from tracing.trace import Trace


class Tracer:
    def __init__(
        self, texture_path: Path, model_path: Path, palette: tuple[Color, ...]
    ):
        self.texture_path: Path = texture_path
        self.model_path: Path = model_path
        self.palette: tuple[Color, ...] = palette

        self.texture: Optional[Image] = None
        self.layers: list[Image] = []

        self.islands: list[Island] = []
        self.segments: list[Segment] = []
        self.traces: list[Trace] = []

    def compute_traces(self) -> list[Trace]:
        self.texture = self.load_texture(self.texture_path)
        self.texture = self.discretize_texture_colors(self.texture)
        self.layers = self.split_colors(self.texture)

        for c, layer in tqdm.tqdm(
            enumerate(self.layers), desc="Island detection", unit="layer"
        ):
            islands: list[Island] = self.detect_islands(layer, c)
            self.islands.extend(islands)

        for island in tqdm.tqdm(
            self.islands, desc="Island segmentation", unit="island"
        ):
            border: list[Segment] = self.resample_border(island)
            self.segments.extend(border)
            fill_slices: list[Segment] = self.compute_fill_slices(island)
            self.segments.extend(fill_slices)

        for segment in tqdm.tqdm(self.segments, desc="3D projection", unit="segment"):
            trace: Trace = self.project_segment_to_3d(segment)
            self.traces.append(trace)

        return self.traces

    def load_texture(self, path: Path) -> Image:
        pass

    def load_model(self, path: Path) -> Mesh:
        pass

    def discretize_texture_colors(self, img: Image) -> Image:
        pass

    def split_colors(self, img: Image) -> list[Image]:
        return []

    def detect_islands(self, img: Image, color: int) -> list[Island]:
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
