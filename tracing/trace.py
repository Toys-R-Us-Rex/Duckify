from dataclasses import dataclass

import numpy as np

from tracing.point_3d import Point3D


@dataclass
class Trace3D:
    """3D drawing path"""

    parent_2d_trace: int

    # Color index
    color: int

    # List of points
    path: list[Point3D]

    def get_polygon(self) -> np.ndarray:
        return np.array([
            p.pos
            for p in self.path
        ])


@dataclass
class Trace2D:
    """2D drawing path on the texture"""

    i: int

    # Color index
    color: int

    # List of points on the texture (Nx2)
    path: np.ndarray
