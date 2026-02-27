from dataclasses import dataclass

import numpy as np


@dataclass
class Trace3D:
    """3D drawing path on a flat surface"""

    # Face normal (3D vector)
    face: np.ndarray

    # Color index
    color: int

    # List of points on the face (Nx3)
    path: np.ndarray


@dataclass
class Trace2D:
    """2D drawing path on the texture"""

    # Color index
    color: int

    # List of points on the texture (Nx2)
    path: np.ndarray
