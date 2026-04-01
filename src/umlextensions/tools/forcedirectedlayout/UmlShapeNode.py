
from logging import Logger
from logging import getLogger

from pyforcedirectedlayout.Point import Point
from pyforcedirectedlayout.Size import Size
from pyforcedirectedlayout.Node import Node

from pyforcedirectedlayout.LayoutTypes import DrawingContext

from umlshapes.shapes.UmlClass import UmlClass

from umlshapes.types.UmlDimensions import UmlDimensions
from umlshapes.types.UmlPosition import UmlPosition


class UmlShapeNode(Node):
    """
    The interface between UML Shapes and the force directed layout module
    """

    def __init__(self, umlClass: UmlClass):

        super().__init__()

        self.logger:    Logger      = getLogger(__name__)
        self._umlClass: UmlClass    = umlClass
        umlPosition:    UmlPosition = self._umlClass.position

        self._location = Point(x=umlPosition.x, y=umlPosition.y)

    @property
    def size(self) -> Size:

        umlDimensions: UmlDimensions = self._umlClass.size

        return Size(width=umlDimensions.width, height=umlDimensions.height)

    @property
    def location(self) -> Point:
        """
        Override base implementation for OglNode
        """
        return self._location

    @location.setter
    def location(self, point: Point):

        umlPosition: UmlPosition = UmlPosition(x=point.x, y=point.y)

        self._umlClass.position = umlPosition

        self._location = point

    def drawNode(self, dc: DrawingContext):
        pass

    def __str__(self) -> str:
        return f'UmlShapeNode - {self._umlClass.modelClass.name}'

    def __repr__(self) -> str:
        return self.__str__()
