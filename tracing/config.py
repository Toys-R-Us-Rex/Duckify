from dataclasses import dataclass

import numpy as np


@dataclass
class TracerConfig:
    debug: bool = False
    """Enable debug visualizations"""

    barycentric_epsilon: float = 1e-8
    """A small epsilon to account for floating-point error in barycentric tests"""

    parallel_normal_epsilon: float = 1e-1
    """A small epsilon to account for floating-point error when comparing parallel face normals"""

    fill_slice_spacing: float = 0.005 # TODO valeur à adapter dynamiquement plus tard ?
    """Gap between filling lines (in UV coordinates)"""

    min_segment_length: float = 0.1
    """Minimum segment length at which recursive edge detection stops (in 3D units)"""

    max_edge_recursion_depth: int = 100
    """Maximum edge detection recursion depth"""

    sharp_edge_threshold: float = np.cos(np.radians(30))
    """Dot-product threshold when considering sharp edges"""

    enable_fill_slicing: bool = True
    """Whether islands filling segments should be computed"""