from dataclasses import dataclass
import numpy as np


@dataclass
class Point3D:
    """3D point on the model"""

    # 3D position
    pos: np.ndarray  # Vec3

    # 3D normal vector
    normal: np.ndarray  # Vec3
