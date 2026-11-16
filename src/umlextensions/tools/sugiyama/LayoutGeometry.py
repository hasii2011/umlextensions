
from dataclasses import dataclass


@dataclass
class LayoutPosition:
    """
    2D coordinate position for layout operations.
    """
    x: int
    y: int


@dataclass
class LayoutSize:
    """
    2D dimensions (width and height) for layout operations.
    """
    width:  int
    height: int
