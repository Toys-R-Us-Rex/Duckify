from dataclasses import dataclass
from typing import Optional

import numpy as np


@dataclass
class Hierarchy:
    """Contour's hierarchical informations"""
    # The index of the current contour in the list of contours
    index: int 
    # The next contour in the image, wich is at the same hierachical level
    next: int
    # The previous contour in the image, wich is at the same hierachical level
    previous : int
    # The first child contour of this current contour
    first_child: int
    # The parent's contour of this current contour
    parent: int
    # Contours in polygon form
    polygon: np.ndarray 
