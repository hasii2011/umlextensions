
from umlshapes.types.UmlDimensions import UmlDimensions
from umlshapes.types.UmlPosition import UmlPosition

from umlextensions.tools.sugiyama.LayoutGeometry import LayoutPosition
from umlextensions.tools.sugiyama.LayoutGeometry import LayoutSize


class LayoutInterfaceNode:
    """
    Interface between UML Shapes and Layout algorithms.
    """
    def __init__(self, umlShape):
        """

        Args:
            umlShape: interfaced UML Shape
        """
        self._umlShape = umlShape

    @property
    def name(self) -> str:
        """
        The class name

        Returns: name of the class
        """
        return self._umlShape.modelClass.name

    @property
    def size(self) -> LayoutSize:
        """
        Return the class size.

        Returns: LayoutSize: (width, height)
        """
        umlDimensions: UmlDimensions = self._umlShape.size
        return LayoutSize(width=umlDimensions.width, height=umlDimensions.height)

    @property
    def position(self) -> LayoutPosition:
        """
        Get class position.

        Returns: The layout position
        """
        umlPosition: UmlPosition = self._umlShape.position
        return LayoutPosition(x=umlPosition.x, y=umlPosition.y)

    @position.setter
    def position(self, layoutPosition: LayoutPosition):
        """
        Set the class position.

        Args:
            layoutPosition
        """
        umlPosition: UmlPosition = UmlPosition(x=layoutPosition.x, y=layoutPosition.y)
        self._umlShape.position = umlPosition
