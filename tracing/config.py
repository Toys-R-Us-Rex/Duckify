from dataclasses import dataclass

import numpy as np


@dataclass
class TracerConfig:
    debug: bool = False
    """Enable debug visualizations"""

    barycentric_epsilon: float = 1e-8
    """A small epsilon to account for floating-point error in barycentric tests"""

    fill_slice_spacing: float = 0.005  # TODO valeur à adapter dynamiquement plus tard ?
    """Gap between filling lines (in UV coordinates)"""

    min_segment_length: float = 1
    """Minimum segment length at which recursive edge detection stops (in 3D units)"""

    max_edge_recursion_depth: int = 100
    """Maximum edge detection recursion depth"""

    sharp_edge_threshold: float = np.cos(np.radians(30))
    """Dot-product threshold when considering sharp edges"""

    enable_fill_slicing: bool = True
    """Whether islands filling segments should be computed"""

    image_size: tuple[int,int] = (800,800)
    """Size format for the loaded texture image"""

    min_island_surface: int = 1  # TODO valeur à adapter dynamiquement plus tard ?
    """Island's surface as treshold to block too small one's"""

    contour_epsilon: float = 1e-8
    """A small epsilon to account for colinearity check in island contour cleaning"""

    contour_simplification_epsilon: float = 0.006
    """An epsilon to account for size refactoring in island contour simplification"""

    parallel_angle: float = np.radians(5)
    """Angle radius threshold when considering too parallel faces"""