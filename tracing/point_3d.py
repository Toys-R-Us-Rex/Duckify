from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class Point3D:
    """3D point on the model"""

    # 3D position
    pos: np.ndarray  # Vec3

    # Face index
    face_idx: int

    # Face normal
    normal: np.ndarray  # Vec3

    # UV coordinates
    uv: np.ndarray  # Vec2

    def with_normal(self, other: Point3D) -> Point3D:
        return Point3D(
            pos=self.pos,
            face_idx=other.face_idx,
            normal=other.normal,
            uv=self.uv
        )
