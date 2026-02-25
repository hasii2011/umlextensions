
from typing import Tuple
from typing import cast

from logging import Logger
from logging import getLogger

from codeallybasic.Position import Position

from umlmodel.enumerations.LinkType import LinkType

from umlshapes.ShapeTypes import LinkableUmlShape
from umlshapes.ShapeTypes import UmlLinkGenre
from umlshapes.ShapeTypes import UmlShapeGenre

from umlshapes.links.UmlInheritance import UmlInheritance

from umlshapes.types.Common import EndPositions
from umlshapes.types.UmlDimensions import UmlDimensions

from umlshapes.types.UmlPosition import UmlPosition
from umlshapes.types.UmlPosition import UmlPositions

from pyorthogonalrouting.Common import Integers
from pyorthogonalrouting.OrthogonalConnectorByProduct import OrthogonalConnectorByProduct

from pyorthogonalrouting.Point import Point
from pyorthogonalrouting.Point import Points
from pyorthogonalrouting.Rectangle import Rectangle
from pyorthogonalrouting.Rect import Rect
from pyorthogonalrouting.Configuration import Configuration
from pyorthogonalrouting.ConnectorPoint import ConnectorPoint
from pyorthogonalrouting.OrthogonalConnector import OrthogonalConnector
from pyorthogonalrouting.OrthogonalConnectorOptions import OrthogonalConnectorOptions

from pyorthogonalrouting.enumerations.Side import Side

from umlextensions.ExtensionsTypes import AssociationName
from umlextensions.ExtensionsTypes import DestinationCardinality
from umlextensions.ExtensionsTypes import DiagnosticInformation
from umlextensions.ExtensionsTypes import InterfaceName
from umlextensions.ExtensionsTypes import LinkInformation
from umlextensions.ExtensionsTypes import SourceCardinality
from umlextensions.IExtensionsFacade import IExtensionsFacade

ANCHOR_POINT_ADJUSTMENT: int = 1    # because line end needs to look like it is right on the line


class OrthogonalConnectorAdapter:
    """
    TODO:  This adapter leaks some of the OrthogonalConnector data types.  Fix this before
    merging to the master branch
    Create a single property call diagnosticInformation

    """
    def __init__(self, extensionsFacade: IExtensionsFacade):

        self.logger: Logger = getLogger(__name__)

        self._extensionsFacade: IExtensionsFacade = extensionsFacade
        self._configuration:    Configuration  = Configuration()

        self._byProducts:   OrthogonalConnectorByProduct = cast(OrthogonalConnectorByProduct, None)

    @property
    def diagnosticInformation(self) -> DiagnosticInformation:
        return self._getDiagnosticInformation()

    # noinspection PyTypeChecker
    @classmethod
    def whichConnectorSide(cls, shape: UmlShapeGenre, anchorPosition: Position) -> Side:

        # shapeX, shapeY           = shape.GetPosition()
        # shapeWidth, shapeHeight  = shape.GetSize()

        umlPosition:   UmlPosition   = shape.position
        umlDimensions: UmlDimensions = shape.size

        shapeX: int = umlPosition.x
        shapeY: int = umlPosition.y
        shapeWidth: int = umlDimensions.width

        minX: int = shapeX
        maxX: int = shapeX + shapeWidth - ANCHOR_POINT_ADJUSTMENT
        minY: int = shapeY

        if anchorPosition.x == minX and anchorPosition.y >= minY:
            side: Side = Side.LEFT
        elif anchorPosition.x == maxX and anchorPosition.y >= minY:
            side = Side.RIGHT
        elif anchorPosition.x > minX and anchorPosition.y == minY:
            side = Side.TOP
        elif anchorPosition.x > minX and anchorPosition.y >= minY:
            side = Side.BOTTOM
        else:
            assert False, 'My algorithm has failed.  boo, hoo hoo'

        return side

    def runConnector(self, oglLink: UmlLinkGenre) -> bool:
        """

        Args:
            oglLink:

        Returns:  `True` the algorithm found a route, else `False`
        """

        sourceSide, destinationSide = self._determineAttachmentSide(umlLink=oglLink)

        sourceRect:      Rect = self._shapeToRect(oglLink.sourceShape)
        destinationRect: Rect = self._shapeToRect(oglLink.destinationShape)

        sourceConnectorPoint:      ConnectorPoint = ConnectorPoint(shape=sourceRect,      side=sourceSide,      distance=self._configuration.sourceEdgeDistance)
        destinationConnectorPoint: ConnectorPoint = ConnectorPoint(shape=destinationRect, side=destinationSide, distance=self._configuration.destinationEdgeDistance)

        options: OrthogonalConnectorOptions = OrthogonalConnectorOptions()
        options.pointA = sourceConnectorPoint
        options.pointB = destinationConnectorPoint

        options.shapeMargin        = self._configuration.shapeMargin
        options.globalBoundsMargin = self._configuration.globalBoundsMargin
        options.globalBounds       = self._configuration.globalBounds

        path: Points     = OrthogonalConnector.route(options=options)

        self._byProducts = OrthogonalConnector.byProduct

        self.logger.info(f'{path}')

        if len(path) == 0:      # noqa
            return False
        else:
            self._deleteTheOldLink(umlLink=oglLink)
            self._createOrthogonalLink(oldLink=oglLink, path=path)
            return True

    def _shapeToRect(self, umlShape: UmlShapeGenre) -> Rect:

        # shapeX, shapeY           = umlShape.GetPosition()
        # shapeWidth, shapeHeight  = umlShape.GetSize()
        umlPosition:   UmlPosition = umlShape.position
        umlDimensions: UmlDimensions = umlShape.size

        rect: Rect = Rect()

        rect.left   = umlPosition.x
        rect.top    = umlPosition.y
        rect.width  = umlDimensions.width
        rect.height = umlDimensions.height

        return rect

    def _determineAttachmentSide(self, umlLink: UmlLinkGenre) -> Tuple[Side, Side]:

        # sourceShape      = oglLink.sourceShape
        # destinationShape = oglLink.destinationShape
        # sourceAnchorPoint:      AnchorPoint = oglLink.sourceAnchor
        # destinationAnchorPoint: AnchorPoint = oglLink.destinationAnchor
        # sourcePosition:      Tuple[int, int] = sourceAnchorPoint.GetPosition()
        # destinationPosition: Tuple[int, int] = destinationAnchorPoint.GetPosition()
        # sourceSide:      Side = OrthogonalConnectorAdapter.whichConnectorSide(shape=sourceShape,      anchorPosition=Position(x=sourcePosition[0], y=sourcePosition[1]))
        # destinationSide: Side = OrthogonalConnectorAdapter.whichConnectorSide(shape=destinationShape, anchorPosition=Position(x=destinationPosition[0], y=destinationPosition[1]))

        sourceShape      = umlLink.sourceShape
        destinationShape = umlLink.destinationShape

        endPoints:           EndPositions = umlLink.endPositions
        sourcePosition:      UmlPosition  = endPoints.fromPosition
        destinationPosition: UmlPosition  = endPoints.toPosition

        self.logger.info(f'{sourcePosition=} {destinationPosition=}')

        sourceSide:      Side = OrthogonalConnectorAdapter.whichConnectorSide(
            shape=sourceShape,
            anchorPosition=Position(x=sourcePosition.x, y=sourcePosition.y)
        )
        destinationSide: Side = OrthogonalConnectorAdapter.whichConnectorSide(
            shape=destinationShape,
            anchorPosition=Position(x=destinationPosition.x, y=destinationPosition.y)
        )

        self.logger.info(f'{sourceSide=} {destinationSide=}')

        return sourceSide, destinationSide

    def _deleteTheOldLink(self, umlLink: UmlLinkGenre):

        self._extensionsFacade.deleteLink(umlLink=umlLink)

    def _createOrthogonalLink(self, oldLink: UmlLinkGenre, path: Points):

        linkType: LinkType = oldLink.modelLink.linkType
        if linkType == LinkType.INHERITANCE:
            umlInheritance:   UmlInheritance   = cast(UmlInheritance, oldLink)  # noqa
            sourceShape:      LinkableUmlShape = umlInheritance.subClass
            destinationShape: LinkableUmlShape = umlInheritance.baseClass
        else:
            sourceShape      = oldLink.sourceShape
            destinationShape = oldLink.destinationShape

        umlPositions: UmlPositions = self._toUmlPositions(path=path)

        linkInformation: LinkInformation = LinkInformation()
        linkInformation.linkType         = linkType
        linkInformation.path             = umlPositions
        linkInformation.sourceShape      = sourceShape
        linkInformation.destinationShape = destinationShape

        if linkType == LinkType.INTERFACE:
            linkInformation.interfaceName = InterfaceName(oldLink.modelLink.name)

        elif linkType == LinkType.ASSOCIATION or linkType == LinkType.COMPOSITION or linkType == LinkType.AGGREGATION:

            linkInformation.associationName        = AssociationName(oldLink.modelLink.name)
            linkInformation.sourceCardinality      = SourceCardinality(oldLink.modelLink.sourceCardinality)
            linkInformation.destinationCardinality = DestinationCardinality(oldLink.modelLink.destinationCardinality)

        self._extensionsFacade.createLink(linkInformation=linkInformation, callback=self._createLinkCallback)

    def _createLinkCallback(self, newLink: UmlLinkGenre):

        self._extensionsFacade.addShape(newLink)
        self._extensionsFacade.refreshFrame()

    def _toUmlPositions(self, path: Points) -> UmlPositions:

        oglPositions: UmlPositions = UmlPositions([])

        for pt in path:
            point:       Point       = cast(Point, pt)
            oglPosition: UmlPosition = UmlPosition(x=point.x, y=point.y)

            oglPositions.append(oglPosition)

        return oglPositions

    def _getDiagnosticInformation(self) -> DiagnosticInformation:
        """
        Don't leak OrthogonalConnector data types

        Returns:  Information that can be used to display why a routing connection failed
        """

        from pyorthogonalrouting.Point import Point
        from pyorthogonalrouting.Point import Points
        from pyorthogonalrouting.Rectangle import Rectangles

        from umlextensions.ExtensionsTypes import Point as DiagnosticPoint
        from umlextensions.ExtensionsTypes import Points as DiagnosticPoints
        from umlextensions.ExtensionsTypes import Rectangle as DiagnosticRectangle
        from umlextensions.ExtensionsTypes import Rectangles as DiagnosticRectangles
        from umlextensions.ExtensionsTypes import IntegerList

        def toDiagnosticPoints(refPoints:  Points) -> DiagnosticPoints:

            diagnosticPts: DiagnosticPoints = DiagnosticPoints([])

            for pt in refPoints:
                point: Point = cast(Point, pt)
                self.logger.info(f'{point=}')

                diagnosticPoint: DiagnosticPoint = DiagnosticPoint(x=point.x, y=point.y)
                diagnosticPts.append(diagnosticPoint)

            return diagnosticPts

        def toDiagnosticRectangle(rectangle: Rectangle) -> DiagnosticRectangle:

            return DiagnosticRectangle(
                left=rectangle.left,
                top=rectangle.top,
                width=rectangle.width,
                height=rectangle.height
            )

        def toIntegerList(integers: Integers) -> IntegerList:

            integerList: IntegerList = IntegerList([])
            for integer in integers:
                integerList.append(integer)

            return integerList

        def toDiagnosticRectangles(rectangles: Rectangles) -> DiagnosticRectangles:

            diagnosticRectangles: DiagnosticRectangles = DiagnosticRectangles([])
            for r in rectangles:
                diagnosticRectangle: DiagnosticRectangle = toDiagnosticRectangle(r)
                diagnosticRectangles.append(diagnosticRectangle)

            return diagnosticRectangles

        diagnosticInformation: DiagnosticInformation = DiagnosticInformation(
            spots=toDiagnosticPoints(refPoints=self._byProducts.spots),
            horizontalRulers=toIntegerList(self._byProducts.hRulers),
            verticalRulers=toIntegerList(self._byProducts.vRulers),
            diagramBounds=toDiagnosticRectangle(self._byProducts.diagramBounds),
            routeGrid=toDiagnosticRectangles(self._byProducts.grid)
        )

        return diagnosticInformation
