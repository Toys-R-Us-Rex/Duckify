from dataclasses import dataclass

import numpy as np


@dataclass
class Segment:
    """2D drawing segment"""

    # First point in UV coordinates
    p1: np.ndarray  # Vec2 (UV)

    # Second point in UV coordinates
    p2: np.ndarray  # Vec2 (UV)

    # Color index
    color: int
