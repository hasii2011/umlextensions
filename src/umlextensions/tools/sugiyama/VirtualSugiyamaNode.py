
from typing import Tuple
from typing import Optional

from umlextensions.tools.sugiyama.SugiyamaNode import SugiyamaNode


class VirtualSugiyamaNode(SugiyamaNode):
    """
    VirtualSugiyamaNode: a virtual node is a node on the Sugiyama graph which
    will not be visible on the diagram.  It is used to reserve space
    for the links drawing.
    """
    def __init__(self, horizontalSpacing: Optional[int] = None):
        super().__init__(horizontalSpacing=horizontalSpacing)

        self.__position: Tuple[int, int] = (0, 0)
        self.__size:     Tuple[int, int] = (1, 1)

    @property
    def size(self) -> Tuple[int, int]:
        """
        Get size of node.

        Returns: A tuple (int, int) : (width, height)
        """
        return self.__size

    @size.setter
    def size(self, newSize: Tuple[int, int]):
        """
        Set the size of the node.

        Args:
            newSize: (width, height) size tuple
        """
        self.__size = newSize

    @property
    def position(self) -> Tuple[int, int]:
        """
        Get node position.

        Returns:    (int, int) : (x, y) in absolute coordinate
        """
        return self.__position

    @position.setter
    def position(self, pos: Tuple[int, int]):
        """
        Set node position.

        Args:
            pos: (x, y) position in absolute coordinates
        """
        self.__position = pos

    def __repr__(self):
        return f'VirtualSugiyamaNode level: {self.level}'
