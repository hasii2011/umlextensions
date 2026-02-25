
from typing import Set
from typing import cast

from logging import Logger
from logging import getLogger

from os import linesep as osLineSep

from umlmodel.Class import Class
from umlmodel.Note import Note

from umlshapes.ShapeTypes import UmlShapeGenre
from umlshapes.ShapeTypes import UmlShapes

from umlshapes.links.UmlLink import UmlLink
from umlshapes.mixins.IdentifierMixin import IdentifierMixin

from umlshapes.shapes.UmlClass import UmlClass
from umlshapes.shapes.UmlNote import UmlNote
from umlshapes.types.Common import EndPositions

from umlshapes.types.UmlDimensions import UmlDimensions
from umlshapes.types.UmlPosition import UmlPosition
from umlshapes.types.UmlPosition import UmlPositions

from umlextensions.output.gml.UnsupportedOperation import UnsupportedOperation

ExportableShapeType = UmlClass | UmlNote
ExportableModelType = Class | Note


class GMLExporter:

    VERSION: str = '2.0.0'

    GRAPH_TOKEN: str = 'graph'

    ID_TOKEN:    str = 'id'
    LABEL_TOKEN: str = 'label'
    NODE_TOKEN:  str = 'node'
    EDGE_TOKEN:  str = 'edge'

    SOURCE_ID_TOKEN: str = 'source'
    TARGET_ID_TOKEN: str = 'target'

    GRAPHICS_TOKEN: str = 'graphics'
    START_TOKEN:    str = '['
    END_TOKEN:      str = ']'

    QUOTE_TOKEN: str = '"'

    LINE_DEFINITION_TOKEN:  str = 'Line'
    POINT_DEFINITION_TOKEN: str = 'point'

    X_POSITION_TOKEN: str = 'x'
    Y_POSITION_TOKEN: str = 'y'
    Z_POSITION_TOKEN: str = 'z'
    WIDTH_TOKEN:      str = 'w'
    HEIGHT_TOKEN:     str = 'h'
    DEPTH_TOKEN:      str = 'd'

    singleTab: str = ''
    doubleTab: str = ''
    tripleTab: str = ''
    quadrupleTab: str = ''
    quintupleTab: str = ''

    def __init__(self):

        self.logger:   Logger = getLogger(__name__)
        self._gml:     str    = ''

        self._prettyPrint: bool = True

    def translate(self, umlShapes: UmlShapes):

        if self._prettyPrint is True:
            GMLExporter.singleTab = '\t'
            GMLExporter.doubleTab = '\t\t'
            GMLExporter.tripleTab = '\t\t\t'
            GMLExporter.quadrupleTab = '\t\t\t\t'
            GMLExporter.quintupleTab = '\t\t\t\t\t'

        gml: str = self._generateGraphStart()
        gml = self._generateNodes(umlShapes, gml)
        gml = self._generateUniqueEdges(umlShapes=umlShapes, gml=gml)

        gml = self._generateGraphTermination(gml)
        self._gml = gml

    @property
    def gml(self):
        return self._gml

    @gml.setter
    def gml(self, theNewValue):
        raise UnsupportedOperation('gml is a read-only property')

    @property
    def prettyPrint(self):
        return self._prettyPrint

    @prettyPrint.setter
    def prettyPrint(self, theNewValue):
        self._prettyPrint = theNewValue

    def write(self, pathToFile: str):

        with open(pathToFile, 'w') as writer:
            writer.write(self._gml)

    def _generateNodes(self, umlShapes: UmlShapes, gml: str) -> str:

        nodeGml: str = ''
        for umlShape in umlShapes:
            if isinstance(umlShape, UmlClass) or isinstance(umlShape, UmlNote):

                identifier:  IdentifierMixin     = cast(IdentifierMixin, umlShape)
                if isinstance(umlShape, UmlClass):
                    modelObject: ExportableModelType = umlShape.modelClass
                elif isinstance(umlShape, UmlNote):
                    modelObject = umlShape.modelNote
                else:
                    assert False, 'Unsupported node type'
                nodeGml = (
                    f'{nodeGml}'
                    f'{GMLExporter.singleTab}{GMLExporter.NODE_TOKEN} {GMLExporter.START_TOKEN}\n'
                    f'{GMLExporter.doubleTab}{GMLExporter.ID_TOKEN} {identifier.id}\n'
                    f'{GMLExporter.doubleTab}{GMLExporter.LABEL_TOKEN} "{modelObject.name}"\n'
                    f'{self._generateNodeGraphicsSection(umlShape)}'
                    f'{GMLExporter.singleTab}{GMLExporter.END_TOKEN}\n'
                )
                self.logger.debug(f'{nodeGml}')
        return f'{gml}{nodeGml}'

    def _generateNodeGraphicsSection(self, umlShape: UmlShapeGenre) -> str:

        # pos = umlShape.GetPosition()
        position: UmlPosition = umlShape.position
        x = position.x
        y = position.y
        z = 0
        dimensions: UmlDimensions = umlShape.size
        w = dimensions.width
        h = dimensions.height
        d = 0
        gml = (
            f'{GMLExporter.doubleTab}{GMLExporter.GRAPHICS_TOKEN} {GMLExporter.START_TOKEN}\n'
            
            f'{GMLExporter.tripleTab}{GMLExporter.X_POSITION_TOKEN} {x}\n'
            f'{GMLExporter.tripleTab}{GMLExporter.Y_POSITION_TOKEN} {y}\n'
            f'{GMLExporter.tripleTab}{GMLExporter.Z_POSITION_TOKEN} {z}\n'
            f'{GMLExporter.tripleTab}{GMLExporter.WIDTH_TOKEN} {w}\n'
            f'{GMLExporter.tripleTab}{GMLExporter.HEIGHT_TOKEN} {h}\n'
            f'{GMLExporter.tripleTab}{GMLExporter.DEPTH_TOKEN} {d}\n'
            f'{GMLExporter.tripleTab}type "rectangle"\n'
            f'{GMLExporter.tripleTab}width 0.12\n'
            f'{GMLExporter.tripleTab}fill "#ff0000"\n'
            f'{GMLExporter.tripleTab}outline "#000000"\n'
            
            f'{GMLExporter.doubleTab}{GMLExporter.END_TOKEN}\n'
        )
        return gml

    def _generateGraphStart(self, graphName: str = 'DefaultGraphName') -> str:

        gml: str = (
            f'{GMLExporter.GRAPH_TOKEN} {GMLExporter.START_TOKEN}\n'
            f'{GMLExporter.singleTab}directed 1\n'
            f'{GMLExporter.singleTab}version  1.0\n'
            f'{GMLExporter.singleTab}label "GML for {graphName}"\n'
            f'{GMLExporter.singleTab}comment "Generated by GML Exporter Version {GMLExporter.VERSION}"\n'
        )

        return gml

    def _generateGraphTermination(self, gml: str) -> str:

        gml = f'{gml}{GMLExporter.END_TOKEN}{osLineSep}'
        return gml

    def _generateUniqueEdges(self, umlShapes: UmlShapes, gml: str) -> str:
        from umlshapes.ShapeTypes import UmlLinks

        linkSet: Set = set()        # Concatenated str link ids;  e.g, 1-2

        for umlShape in umlShapes:
            if isinstance(umlShape, UmlClass) or isinstance(umlShape, UmlNote):
                links: UmlLinks = umlShape.links
                self.logger.info(f'links: {links}')
                for umlLink in links:
                    srcShapeId:  str = umlLink.sourceShape.id
                    destShapeId: str = umlLink.destinationShape.id
                    linkIds:   str = f'{srcShapeId}-{destShapeId}'
                    if linkIds not in linkSet:
                        gml = self.__generateUniqueEdge(umlLink=umlLink, gml=gml)
                        linkSet.add(linkIds)

        return gml

    def __generateUniqueEdge(self, umlLink: UmlLink, gml: str) -> str:

        srcShapeId:  str = umlLink.sourceShape.id
        destShapeId: str = umlLink.destinationShape.id

        gml = (
            f'{gml}'
            f'{GMLExporter.singleTab}{GMLExporter.EDGE_TOKEN} {GMLExporter.START_TOKEN}\n'
            f'{GMLExporter.doubleTab}{GMLExporter.ID_TOKEN} {umlLink.id}\n'
            f'{GMLExporter.doubleTab}{GMLExporter.SOURCE_ID_TOKEN} {srcShapeId}\n'
            f'{GMLExporter.doubleTab}{GMLExporter.TARGET_ID_TOKEN} {destShapeId}\n'
            f'{self.__generateEdgeGraphicsSection(umlLink=umlLink)}'
            f'{GMLExporter.singleTab}{GMLExporter.END_TOKEN}\n'
        )

        return gml

    def __generateEdgeGraphicsSection(self, umlLink: UmlLink) -> str:

        endPositions:     EndPositions = umlLink.endPositions
        controlPositions: UmlPositions = umlLink.controlPositions

        edgeGml: str = (
            f'{GMLExporter.doubleTab}{GMLExporter.GRAPHICS_TOKEN} {GMLExporter.START_TOKEN}\n'
            f'{GMLExporter.tripleTab}type "line"\n'
            f'{GMLExporter.tripleTab}arrow "last"\n'
            f'{GMLExporter.tripleTab}{GMLExporter.LINE_DEFINITION_TOKEN} {GMLExporter.START_TOKEN}\n'
            f'{self.__generatePoint(endPositions.fromPosition)}'
            f'{self.__generatePoints(controlPositions)}'
            f'{self.__generatePoint(endPositions.toPosition)}'
            f'{GMLExporter.tripleTab}{GMLExporter.END_TOKEN}\n'
            f'{GMLExporter.doubleTab}{GMLExporter.END_TOKEN}\n'
        )

        return edgeGml

    def __generatePoints(self, controlPoints) -> str:

        pointsGml: str = ''
        for umlPosition in controlPoints:
            pointsGml = (
                f'{pointsGml}{self.__generatePoint(umlPosition)}'
            )

        return pointsGml

    def __generatePoint(self, umlPosition: UmlPosition) -> str:

        # position: Tuple[int, int] = linePoint.GetPosition()

        x:        int = umlPosition.x
        y:        int = umlPosition.y
        z:        int = 0
        pointGml: str = (
            f'{GMLExporter.quadrupleTab}{GMLExporter.POINT_DEFINITION_TOKEN} {GMLExporter.START_TOKEN}\n'
            f'{GMLExporter.quintupleTab}{GMLExporter.X_POSITION_TOKEN} {x}\n'
            f'{GMLExporter.quintupleTab}{GMLExporter.Y_POSITION_TOKEN} {y}\n'
            f'{GMLExporter.quintupleTab}{GMLExporter.Z_POSITION_TOKEN} {z}\n'
            f'{GMLExporter.quadrupleTab}{GMLExporter.END_TOKEN}\n'
        )

        return pointGml
