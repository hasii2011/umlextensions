
from typing import cast
from typing import List
from typing import NewType

from logging import Logger
from logging import getLogger

from networkx import Graph
from networkx import spring_layout

from umlshapes.ShapeTypes import UmlShapes
from umlshapes.ShapeTypes import UmlShapeGenre
from umlshapes.ShapeTypes import LinkableUmlShape

from umlshapes.frames.UmlFrame import UmlFrame

from umlshapes.links.UmlLink import UmlLink

from umlshapes.shapes.UmlClass import UmlClass

from umlshapes.types.UmlPosition import UmlPosition

from umlextensions.IExtensionsFacade import IExtensionsFacade

from umlextensions.extensiontypes.ExtensionDataTypes import Author
from umlextensions.extensiontypes.ExtensionDataTypes import ExtensionName
from umlextensions.extensiontypes.ExtensionDataTypes import Version

from umlextensions.tools.BaseToolExtension import BaseToolExtension
from umlextensions.tools.diagramarranger.ForceDirectedMethod import ForceDirectedMethod

UmlClasses = NewType('UmlClasses', List[UmlClass])      # This seems like a UML Shape oversight

class ToolDiagramArranger(BaseToolExtension):

    def __init__(self, extensionsFacade: IExtensionsFacade):

        super().__init__(extensionsFacade=extensionsFacade)
        self.logger: Logger = getLogger(__name__)

        self._name    = ExtensionName('Diagram Arranger')
        self._author  = Author('Humberto A. Sanchez II')
        self._version = Version('1.0')

    def setOptions(self) -> bool:
        return True

    def doAction(self):

        self.logger.info(f'Begin Force Directed Layout')
        selectedUmlShapes: UmlShapes = self._frameInformation.selectedUmlShapes

        self._applySpringLayout(umlShapes=selectedUmlShapes)
        self.logger.info('End Force Directed Layout')

    def _applySpringLayout(self, umlShapes: UmlShapes, scale: int = 400):
        """
        Applies a NetworkX spring layout to the shapes in the provided UmlFrame.

        Position nodes using Fruchterman-Reingold force-directed algorithm.

        The algorithm simulates a force-directed representation of the network
        * treating edges as springs holding nodes close,
        * While treating nodes as repelling objects, sometimes called an anti-gravity force.
        * The simulation continues until the positions are close to an equilibrium.

        Args:
            umlShapes:
            scale:       The scale factor to adjust the layout to the canvas size
        """

        networkXGraph: Graph      = Graph()
        umlClasses: UmlClasses    = UmlClasses([])
        umlLinks:   List[UmlLink] = []

        # The maximum number of iterations for the algorithm
        iterations: int = self._preferences.iterations
        # k is the optimal distance between nodes; larger values to move nodes farther apart
        k: float = self._preferences.optimalNodeDistance
        layoutMethod: ForceDirectedMethod = self._preferences.layoutMethod

        for shape in umlShapes:

            if isinstance(shape, UmlShapeGenre):
                umlClass: UmlClass = cast(UmlClass, shape)
                networkXGraph.add_node(umlClass)
                umlClasses.append(umlClass)

            elif isinstance(shape, UmlLink):
                umlLink: UmlLink = cast(UmlLink, shape)  # noqa
                fromClass: LinkableUmlShape = umlLink.sourceShape
                toClass:   LinkableUmlShape = umlLink.destinationShape
                if fromClass and toClass:
                    networkXGraph.add_edge(fromClass, toClass)
                    umlLinks.append(umlLink)

        # This returns a dictionary mapping nodes to (x, y) coordinates
        positionDictionary: dict = spring_layout(networkXGraph, k=k, iterations=iterations, method=layoutMethod.value)

        self.logger.debug(f'{positionDictionary}')

        # Define a center for the layout (e.g., the center of the frame or a fixed point)
        layoutCenter: UmlPosition = self._preferences.layoutCenter

        # Update the shape positions
        for shape, coordinates in positionDictionary.items():
            # networkx coordinates are typically normalized or centered around (0,0)
            # Scale and shift them to fit your diagram's coordinate system
            newX = layoutCenter.x + int(coordinates[0] * scale)
            newY = layoutCenter.y + int(coordinates[1] * scale)

            umlClassToPosition: UmlClass = shape
            umlClassToPosition.position  = UmlPosition(x=newX, y=newY)

        for link in umlLinks:
            optimalLink: UmlLink = link
            optimalLink.optimizeLink()

        # Refresh the frame to show the changes
        umlFrame: UmlFrame = self._frameInformation.umlFrame
        umlFrame.redrawShapes()
        umlFrame.refresh()

        self.logger.info("Spring layout applied successfully.")
