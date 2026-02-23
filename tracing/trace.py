from dataclasses import dataclass

from point_3d import Point3D


@dataclass
class Trace:
    """3D drawing segment"""

    # First 3D point
    p1: Point3D

    # Second 3D point
    p2: Point3D

    # Color index
    color: int
