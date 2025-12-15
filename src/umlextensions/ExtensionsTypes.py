#
#  These types are visible to the extension adapter and the
#  implementor of the adapter
#
from typing import List
from typing import NewType
from typing import Tuple
from typing import cast
from typing import Callable

from dataclasses import dataclass
from dataclasses import field

from umlshapes.ShapeTypes import UmlLinkGenre
from umlshapes.types.UmlPosition import UmlPositions
from wx import ClientDC

from umlmodel.enumerations.LinkType import LinkType

from umlshapes.ShapeTypes import LinkableUmlShape
from umlshapes.frames.UmlFrame import UmlFrame

from umlshapes.ShapeTypes import UmlShapes
from umlshapes.ShapeTypes import umlShapesFactory

from umlio.IOTypes import UmlDocumentType

InterfaceName          = NewType('InterfaceName', str)
AssociationName        = NewType('AssociationName', str)
SourceCardinality      = NewType('SourceCardinality', str)
DestinationCardinality = NewType('DestinationCardinality', str)

@dataclass
class FrameSize:
    """
    The strategy is to provide minimal information to the extensions
    we do not want them to not abuse it.
    """
    width:  int = -1
    height: int = -1


def createFrameSizeFactory() -> FrameSize:
    """
    Factory method to create  the OglClasses data structure;

    Returns:  A new data structure
    """
    return FrameSize()


@dataclass
class FrameInformation:
    """
    The document title is the name of the frame
    """
    umlFrame:           UmlFrame   = cast(UmlFrame, None)
    frameActive:        bool       = False
    selectedUmlShapes:  UmlShapes  = field(default_factory=umlShapesFactory)
    frameSize:          FrameSize  = field(default_factory=createFrameSizeFactory)
    clientDC:           ClientDC   = cast(ClientDC, None)
    diagramTitle:       str        = ''
    diagramType:        UmlDocumentType = UmlDocumentType.NOT_SET


FrameInformationCallback  = Callable[[FrameInformation], None]
FrameSizeCallback         = Callable[[FrameSize], None]
SelectedUmlShapesCallback = Callable[[UmlShapes], None]

NO_INTEGER: int = cast(int, None)


@dataclass
class ShapeBoundaries:
    minX: int = NO_INTEGER
    minY: int = NO_INTEGER
    maxX: int = NO_INTEGER
    maxY: int = NO_INTEGER


ObjectBoundaryCallback = Callable[[ShapeBoundaries], None]

@dataclass(eq=True)
class Point:
    """
    A point in space.
    """
    x: int = NO_INTEGER
    y: int = NO_INTEGER

    def toTuple(self) -> Tuple[int, int]:
        return self.x, self.y

    def __hash__(self) -> int:
        return hash((self.x, self.y))


IntegerList = NewType('IntegerList', List[int])
Points      = NewType('Points',      List[Point])

@dataclass
class Rectangle:
    left:   int = 0
    top:    int = 0
    width:  int = 0
    height: int = 0


Rectangles = NewType('Rectangles', List[Rectangle])

@dataclass
class DiagnosticInformation:

    horizontalRulers: IntegerList
    verticalRulers:   IntegerList
    diagramBounds:    Rectangle
    spots:            Points
    routeGrid:        Rectangles

def umlPositionsFactory() -> UmlPositions:
    return UmlPositions([])

@dataclass
class LinkInformation:
    """
    The field interfaceName is only valid when linkType is PyutLinkType.INTERFACE
    The fields
        associationName
        sourceCardinality
        destinationCardinality
    are valid only when linkType is  one of
        PyutLinkType.ASSOCIATION
        PyutLinkType.COMPOSITION
        PyutLinkType.AGGREGATION
    """
    linkType:               LinkType                = cast(LinkType, None)
    path:                   UmlPositions            = field(default_factory=umlPositionsFactory)
    sourceShape:            LinkableUmlShape        = cast(LinkableUmlShape, None)
    destinationShape:       LinkableUmlShape        = cast(LinkableUmlShape, None)
    interfaceName:          InterfaceName           = cast(InterfaceName, None)
    associationName:        AssociationName         = cast(AssociationName, None)
    sourceCardinality:      SourceCardinality       = cast(SourceCardinality, None)
    destinationCardinality: DestinationCardinality  = cast(DestinationCardinality, None)


CreatedLinkCallback = Callable[[UmlLinkGenre], None]
