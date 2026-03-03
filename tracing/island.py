from dataclasses import dataclass, field

import numpy as np


@dataclass
class Island:
    """Bounded color island on the texture"""

    # Color index
    color: int

    # Border polygon in UV coordinates
    outer_border: np.ndarray  # Nx2
    # List of inner(s) border(s)
    inner_borders: list[np.ndarray] = field(default_factory=list)  # Nx2
