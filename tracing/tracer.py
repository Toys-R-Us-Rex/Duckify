from pathlib import Path
from typing import Optional

import numpy as np
import tqdm
from PIL.Image import Image

from color import Color
from island import Island
from point_3d import Point3D
from segment import Segment
from trace import Trace


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
        self.texture = self.discretize_texture_colors(self.texture, self.palette)
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
        return Image()

    def load_model(self, path: Path) -> "Mesh":
        return None

    def discretize_texture_colors(self, img: Image, palette: tuple[Color, ...]) -> Image:
        return img

    def split_colors(self, img: Image) -> list[Image]:
        return [img, img, img]

    def detect_islands(self, img: Image, color: int) -> list[Island]:
        return [
            Island(color, np.array([
                [0, 0],
                [1, 0],
                [1, 1],
                [0, 1],
            ]))
        ]

    def resample_border(self, island: Island) -> list[Segment]:
        return [
            Segment(np.array([0, 0]), np.array([1, 0]), island.color),
            Segment(np.array([1, 0]), np.array([1, 1]), island.color),
            Segment(np.array([1, 1]), np.array([0, 1]), island.color),
            Segment(np.array([0, 1]), np.array([0, 0]), island.color),
        ]

    def compute_fill_slices(self, island: Island) -> list[Segment]:
        return [
            Segment(np.array([0, 0]), np.array([1, 1]), island.color)
        ]

    def resample_fill_segment(self, segment: Segment) -> list[Segment]:
        return [
            segment
        ]

    def project_segment_to_3d(self, segment: Segment) -> Trace:
        return Trace(
            p1=self.interpolate_position(segment.p1),
            p2=self.interpolate_position(segment.p2),
            color=segment.color
        )

    def interpolate_position(self, uv_pos: np.ndarray) -> Point3D:
        return Point3D(
            pos=np.array([uv_pos[0], uv_pos[1], 0]),
            normal=np.array([0, 0, 1])
        )
