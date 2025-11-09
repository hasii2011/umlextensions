from typing import cast

from umlshapes.mixins.TopLeftMixin import TopLeftMixin
from umlshapes.types.UmlDimensions import UmlDimensions
from umlshapes.types.UmlPosition import UmlPosition


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

    def getSize(self):
        """
        Return the class size.

        Returns: (int, int): tuple (width, height)
        """
        umlDimensions: UmlDimensions = cast(TopLeftMixin, self._umlShape).size
        # return self._umlShape.GetSize()
        return umlDimensions.width, umlDimensions.height

    def getPosition(self):
        """
        Get class position.

        Returns: (int, int): tuple (x, y) coordinates
        """
        umlPosition: UmlPosition = cast(TopLeftMixin, self._umlShape).position
        # return self._umlShape.GetPosition()
        return umlPosition.x, umlPosition.y

    def setPosition(self, x: int, y: int):
        """
        Set the class position.

        Args:
            x: absolute coordinates
            y: absolute coordinates
        """
        umlPosition: UmlPosition = UmlPosition(x=x, y=y)
        # self._umlShape.SetPosition(x, y)
        cast(TopLeftMixin, self._umlShape).position = umlPosition

    def getName(self) -> str:
        """
        Get the name of the class.

        Returns: name of the class
        """
        # return self._oglObject.pyutObject.name
        return self._umlShape.pyutClass.name
