from dataclasses import dataclass


@dataclass
class TracerConfig:
    debug: bool = False
    """Enable debug visualizations"""

    barycentric_epsilon: float = 1e-8
    """A small epsilon to account for floating-point error in barycentric tests"""

    parallel_normal_epsilon: float = 1e-6
    """A small epsilon to account for floating-point error when comparing parallel face normals"""
