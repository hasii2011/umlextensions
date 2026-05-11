
from typing import List
from typing import cast
from typing import NewType

from logging import Logger
from logging import getLogger

from dataclasses import dataclass

from networkx import Graph
from networkx import arf_layout
from networkx import forceatlas2_layout
from networkx import planar_layout
from networkx import spring_layout

from umlshapes.ShapeTypes import LinkableUmlShape
from umlshapes.ShapeTypes import UmlShapeGenre
from umlshapes.ShapeTypes import UmlShapes

from umlshapes.frames.UmlFrame import UmlFrame

from umlshapes.links.UmlLink import UmlLink

from umlshapes.shapes.UmlClass import UmlClass

from umlshapes.types.UmlPosition import UmlPosition

from umlextensions.ExtensionsPreferences import ExtensionsPreferences

from umlextensions.tools.diagramarranger.configpanels.ForceDirectedMethod import ForceDirectedMethod

SelectedClasses = NewType('SelectedClasses', List[UmlClass])
SelectedLinks   = NewType('SelectedLinks',   List[UmlLink])

@dataclass
class SelectionResults:
    updatedGraph:    Graph
    selectedClasses: SelectedClasses
    selectedLinks:   SelectedLinks

class LayoutAlgorithms:
    """

    """
    def __init__(self):

        self.logger:      Logger                 = getLogger(__name__)
        self._preferences: ExtensionsPreferences = ExtensionsPreferences()

    def applyForceAtlas2Layout(self, umlFrame: UmlFrame, umlShapes: UmlShapes):
        """

        Args:
            umlFrame:       The UML frame we are working on
            umlShapes:      The shapes we need to consider
        """
        self.logger.info("Starting Force Atlas2 layout.")

        preferences: ExtensionsPreferences = self._preferences

        maxIterations:         int   = preferences.atlasMaxIterations
        jitterTolerance:       float = preferences.jitterTolerance
        scalingRatio:          float = preferences.scalingRatio
        gravity:               float = preferences.gravity
        distributedAction:     bool  = preferences.distributedAction
        strongGravity:         bool  = preferences.strongGravity
        logarithmicAttraction: bool  = preferences.logarithmicAttraction
        preventShapeCrowding:  bool  = preferences.preventShapeCrowding

        networkXGraph: Graph = Graph()

        selectionResults: SelectionResults = self._selectShapesToLayout(networkXGraph, umlShapes)

        if preventShapeCrowding:
            nodeSizes: dict = {}
            for shape in selectionResults.selectedClasses:
                # Use width, height, or a representative value (like max)
                nodeSizes[shape] = max(shape.size.width, shape.size.height)
        else:
            nodeSizes = None    # type: ignore

        networkXGraph = selectionResults.updatedGraph
        positionDictionary: dict = forceatlas2_layout(
            networkXGraph,
            max_iter=maxIterations,
            jitter_tolerance=jitterTolerance,
            scaling_ratio=scalingRatio,
            gravity=gravity,
            distributed_action=distributedAction,
            strong_gravity=strongGravity,
            linlog=logarithmicAttraction,
            node_size=nodeSizes,
        )

        self._repositionTheShapes(
            positionDictionary=positionDictionary,
            selectedLinks=selectionResults.selectedLinks,
            frameScale=50,
            umlFrame=umlFrame
        )

        self.logger.info(f'Force Atlas2 layout successfully applied.')

    def applyPlanarLayout(self, umlFrame: UmlFrame, umlShapes: UmlShapes):
        """

        Args:
            umlFrame:       The UML frame we are working on
            umlShapes:      The shapes we need to consider
        """
        self.logger.info("Starting Planar layout.")

        planarLayoutFrameScaleFactor: int = self._preferences.planarFrameScaleFactor
        positionsScale:               int = self._preferences.positionsScale

        networkXGraph: Graph = Graph()

        selectionResults: SelectionResults = self._selectShapesToLayout(networkXGraph, umlShapes)

        networkXGraph = selectionResults.updatedGraph
        positionDictionary: dict = planar_layout(networkXGraph, scale=positionsScale)

        self._repositionTheShapes(
            positionDictionary=positionDictionary,
            selectedLinks=selectionResults.selectedLinks,
            frameScale=planarLayoutFrameScaleFactor,
            umlFrame=umlFrame
        )

        self.logger.info(f'Planar layout successfully applied.')

    def applyArfLayout(self, umlFrame: UmlFrame, umlShapes: UmlShapes):
        """

        Args:
            umlFrame:       The UML frame we are working on
            umlShapes:      The shapes we need to consider
        """
        self.logger.info("Starting Attractive and Repulsive Forces layout.")

        preferences: ExtensionsPreferences = self._preferences

        maxIterations:     int   = preferences.arfMaxIterations
        springStrength:    float = preferences.arfSpringStrength
        iterationStepSize: float = preferences.iterationStepSize
        frameScale:        int   = preferences.arfFrameScaleFactor

        networkXGraph: Graph = Graph()

        selectionResults: SelectionResults = self._selectShapesToLayout(networkXGraph, umlShapes)

        networkXGraph = selectionResults.updatedGraph
        #
        # a - Strength of springs between the connected shapes. Should be larger than 1. The
        # greater 'a', the more separation between unconnected sub clusters.
        #
        # max_iter - The maximum iterations before stopping the algorithm
        #
        # dt - It is the step size used during the force-directed simulation  dt determines how much the shapes are allowed to move in a single iteration
        # A larger dt makes nodes move further per iteration;  faster convergence;  too large may become unstable;
        # A smaller dt makes the simulation more stable and precise, but require more iterations (max_iter) to reach an equilibrium.
        #
        positionDictionary: dict = arf_layout(
            networkXGraph,
            a=springStrength,
            dt=iterationStepSize,
            max_iter=maxIterations
        )

        self._repositionTheShapes(
            positionDictionary=positionDictionary,
            selectedLinks=selectionResults.selectedLinks,
            frameScale=frameScale,
            umlFrame=umlFrame
        )

        self.logger.info(f'Attractive and Repulsive Forces layout successfully applied.')

    def applySpringLayout(self, umlFrame: UmlFrame, umlShapes: UmlShapes):
        """
        Applies a NetworkX spring layout to the shapes in the provided UmlFrame.

        Position nodes using Fruchterman-Reingold force-directed algorithm.

        The algorithm simulates a force-directed representation of the network
        * It treats edges as springs holding the shapes close,
        * It treats the shapes as repelling objects, sometimes called an antigravity force.
        * The simulation continues until the positions are close to an equilibrium.

        Args:
            umlFrame:       The UML frame we are working on
            umlShapes:      The shapes we need to consider
        """
        self.logger.info("Starting Spring layout.")

        preferences: ExtensionsPreferences = self._preferences

        networkXGraph: Graph = Graph()

        iterations: int   = preferences.iterations              # The maximum number of iterations for the algorithm
        k:          float = preferences.optimalNodeDistance     # Optimal distance between nodes; larger values space nodes farther apart
        scale:      int   = preferences.frameSizeScaleFactor    # Factor that adjusts the layout to the UML Frame size

        layoutMethod: ForceDirectedMethod = preferences.layoutMethod  # The method used to compute the layout

        selectionResults: SelectionResults = self._selectShapesToLayout(networkXGraph, umlShapes)

        networkXGraph = selectionResults.updatedGraph
        # This returns a dictionary mapping nodes to (x, y) coordinates
        positionDictionary: dict = spring_layout(
            networkXGraph,
            k=k,
            iterations=iterations,
        )

        self.logger.debug(f'{positionDictionary}')

        self._repositionTheShapes(positionDictionary, selectionResults.selectedLinks, scale, umlFrame)

        self.logger.info(f'Spring layout successfully applied. {layoutMethod=} {iterations=} optimalNodeDistance={k}')

    def _repositionTheShapes(self, positionDictionary: dict, selectedLinks: SelectedLinks, frameScale: int, umlFrame: UmlFrame):
        """

        Args:
            positionDictionary: The positions returned by the executed layout algorithm
            selectedLinks:      The selected links
            frameScale:         networkx coordinates are centered around (0,0);  This value shifts them to fit
            our UML Diagram coordinate system
            umlFrame:           The diagram frame we are working on
        """
        # Define a center for the layout (e.g., the center of the frame or a fixed point)
        layoutCenter: UmlPosition = self._preferences.layoutCenter

        # Update the shape positions
        for shape, coordinates in positionDictionary.items():
            newX = layoutCenter.x + int(coordinates[0] * frameScale)
            newY = layoutCenter.y + int(coordinates[1] * frameScale)

            umlClassToPosition: UmlClass = shape
            umlClassToPosition.position = UmlPosition(x=newX, y=newY)

        for link in selectedLinks:
            optimalLink: UmlLink = link
            optimalLink.optimizeLink()

        # Refresh the frame to show the changes
        # umlFrame: UmlFrame = self._frameInformation.umlFrame
        umlFrame.redrawShapes()
        umlFrame.refresh()

    def _selectShapesToLayout(self, networkXGraph: Graph, umlShapes: UmlShapes) -> SelectionResults:
        """

        Args:
            networkXGraph:  The graph to populate
            umlShapes:      The shapes to selected from

        Returns: A tuple of the updated networkx graph and the selected shapes and links

        """
        umlClasses: SelectedClasses = SelectedClasses([])
        umlLinks:   SelectedLinks   = SelectedLinks([])

        for shape in umlShapes:

            if isinstance(shape, UmlShapeGenre):
                umlClass: UmlClass = cast(UmlClass, shape)
                networkXGraph.add_node(umlClass)
                umlClasses.append(umlClass)

            elif isinstance(shape, UmlLink):
                umlLink: UmlLink = cast(UmlLink, shape)  # noqa
                fromClass: LinkableUmlShape = umlLink.sourceShape
                toClass: LinkableUmlShape = umlLink.destinationShape
                if fromClass and toClass:
                    networkXGraph.add_edge(fromClass, toClass)
                    umlLinks.append(umlLink)

        return SelectionResults(
            updatedGraph=networkXGraph,
            selectedClasses=umlClasses,
            selectedLinks=umlLinks
        )
