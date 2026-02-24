from dataclasses import dataclass

import numpy as np


@dataclass
class Island:
    """Bounded color island on the texture"""

    idx: int

    # Color index
    color: int

    # Border polygon in UV coordinates
    border: np.ndarray  # Nx2
