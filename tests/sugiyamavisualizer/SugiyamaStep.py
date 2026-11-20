"""
Phase-by-phase snapshot model and stepper for the Sugiyama hierarchical layout algorithm.
"""

from dataclasses import dataclass
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import cast

from umlmodel.Class import Class
from umlmodel.Link import Link
from umlmodel.enumerations.LinkType import LinkType

from umlshapes.ShapeTypes import UmlShapes
from umlshapes.ShapeTypes import umlShapesFactory
from umlshapes.frames.ClassDiagramFrame import ClassDiagramFrame
from umlshapes.links.UmlAssociation import UmlAssociation
from umlshapes.links.UmlInheritance import UmlInheritance
from umlshapes.shapes.UmlClass import UmlClass
from umlshapes.types.UmlDimensions import UmlDimensions
from umlshapes.types.UmlPosition import UmlPosition

from umlextensions.IExtensionsFacade import IExtensionsFacade
from umlextensions.tools.sugiyama.RealSugiyamaNode import RealSugiyamaNode
from umlextensions.tools.sugiyama.Sugiyama import Levels
from umlextensions.tools.sugiyama.Sugiyama import NodeList
from umlextensions.tools.sugiyama.Sugiyama import Nodes
from umlextensions.tools.sugiyama.Sugiyama import Sugiyama
from umlextensions.tools.sugiyama.SugiyamaConstants import H_SPACE
from umlextensions.tools.sugiyama.SugiyamaConstants import LEFT_MARGIN
from umlextensions.tools.sugiyama.SugiyamaConstants import UP_MARGIN
from umlextensions.tools.sugiyama.SugiyamaConstants import V_SPACE
from umlextensions.tools.sugiyama.SugiyamaLink import SugiyamaLink
from umlextensions.tools.sugiyama.VirtualSugiyamaNode import VirtualSugiyamaNode

from tests.sugiyamavisualizer.SugiyamaDataSet import SugiyamaDataSet
from tests.sugiyamavisualizer.SugiyamaDataSet import SugiyamaEdgeSpec
from tests.sugiyamavisualizer.SugiyamaDataSet import SugiyamaNodeSpec

VIRTUAL_NODE_DISPLAY_SIZE: int = 22


@dataclass(frozen=True)
class SugiyamaNodeSnapshot:
    """
    Immutable snapshot of a single node (real or virtual) at a Sugiyama step.
    """
    name:       str
    isVirtual:  bool
    level:      int
    index:      int
    barycenter: float
    x:          int
    y:          int
    width:      int
    height:     int


@dataclass(frozen=True)
class SugiyamaLinkSnapshot:
    """
    Immutable snapshot of a single link and its control points at a Sugiyama step.
    """
    sourceName:     str
    targetName:     str
    linkType:       LinkType
    isHierarchical: bool
    controlPoints:  List[Tuple[int, int]]


@dataclass(frozen=True)
class SugiyamaStepSnapshot:
    """
    Immutable snapshot of the entire Sugiyama graph state after a phase.
    """
    stepIndex:        int
    phaseName:        str
    description:      str
    levels:           List[List[SugiyamaNodeSnapshot]]
    unleveledNodes:   List[SugiyamaNodeSnapshot]
    links:            List[SugiyamaLinkSnapshot]
    crossingCount:    int
    virtualNodeCount: int


class SugiyamaStepper:
    """
    Executes Sugiyama phase-by-phase on a preset dataset and records step snapshots.
    """

    def __init__(
        self,
        dataSet:          SugiyamaDataSet,
        diagramFrame:     ClassDiagramFrame,
        extensionsFacade: IExtensionsFacade,
    ):
        """
        Construct and run the Sugiyama stepper for the given preset dataset.

        Args:
            dataSet: Preset graph specification.
            diagramFrame: Hidden ClassDiagramFrame hosting real UML shapes.
            extensionsFacade: Extensions facade instance.
        """
        self._dataSet:          SugiyamaDataSet   = dataSet
        self._diagramFrame:     ClassDiagramFrame = diagramFrame
        self._extensionsFacade: IExtensionsFacade = extensionsFacade
        self._steps:            List[SugiyamaStepSnapshot] = []

        self._buildSnapshots()

    @property
    def steps(self) -> List[SugiyamaStepSnapshot]:
        """
        Return the recorded phase-by-phase snapshots.

        Returns:
            Ordered list of SugiyamaStepSnapshot instances.
        """
        return self._steps

    def _buildSnapshots(self):
        """
        Populate the UML frame with preset shapes and record each Sugiyama phase.
        """
        self._diagramFrame.umlDiagram.DeleteAllShapes()

        umlClasses: Dict[str, UmlClass] = {}
        umlShapes:  UmlShapes           = umlShapesFactory()

        nodeSpec: SugiyamaNodeSpec
        for nodeSpec in self._dataSet.nodes:
            modelClass: Class    = Class(name=nodeSpec.name)
            umlClass:   UmlClass = UmlClass(
                modelClass=modelClass,
                size=UmlDimensions(width=nodeSpec.width, height=nodeSpec.height)
            )
            umlClass.position = UmlPosition(x=nodeSpec.x, y=nodeSpec.y)
            self._diagramFrame.umlDiagram.AddShape(umlClass)
            umlClass.SetCanvas(self._diagramFrame)
            umlClasses[nodeSpec.name] = umlClass
            umlShapes.append(umlClass)

        edgeSpec: SugiyamaEdgeSpec
        for edgeSpec in self._dataSet.edges:
            if edgeSpec.sourceName not in umlClasses or edgeSpec.targetName not in umlClasses:
                continue

            srcClass: UmlClass = umlClasses[edgeSpec.sourceName]
            dstClass: UmlClass = umlClasses[edgeSpec.targetName]

            if edgeSpec.linkType == LinkType.INHERITANCE:
                inhLink: Link           = Link(linkType=LinkType.INHERITANCE, source=srcClass.modelClass, destination=dstClass.modelClass)
                umlInh:  UmlInheritance = UmlInheritance(link=inhLink, baseClass=dstClass, subClass=srcClass)
                umlInh.SetCanvas(self._diagramFrame)
                umlInh.MakeLineControlPoints(2)
                srcClass.addLink(umlLink=umlInh, destinationClass=dstClass)
                self._diagramFrame.umlDiagram.AddShape(umlInh)
                umlShapes.append(umlInh)
            else:
                assocLink: Link           = Link(linkType=LinkType.ASSOCIATION, source=srcClass.modelClass, destination=dstClass.modelClass)
                umlAssoc:  UmlAssociation = UmlAssociation(link=assocLink)
                umlAssoc.SetCanvas(self._diagramFrame)
                umlAssoc.MakeLineControlPoints(2)
                srcClass.addLink(umlLink=umlAssoc, destinationClass=dstClass)
                self._diagramFrame.umlDiagram.AddShape(umlAssoc)
                umlShapes.append(umlAssoc)

        self._steps.append(self._snapshotInitial(stepIndex=0))

        sugiyama: Sugiyama = Sugiyama(umlFrame=self._diagramFrame, extensionsFacade=self._extensionsFacade)
        sugiyama.buildGraph(umlShapes=umlShapes)
        self._steps.append(
            self._snapshotFromSugiyama(
                sugiyama=sugiyama,
                stepIndex=1,
                phaseName='buildGraph',
                description='Wrapped UML classes and links into RealSugiyamaNode and SugiyamaLink objects.',
                usePreviewPositions=False
            )
        )

        sugiyama.levelFind()
        self._steps.append(
            self._snapshotFromSugiyama(
                sugiyama=sugiyama,
                stepIndex=2,
                phaseName='levelFind',
                description='Assigned hierarchical nodes to top-down levels.',
                usePreviewPositions=True
            )
        )

        sugiyama.addVirtualNodes()
        self._steps.append(
            self._snapshotFromSugiyama(
                sugiyama=sugiyama,
                stepIndex=3,
                phaseName='addVirtualNodes',
                description='Inserted VirtualSugiyamaNode placeholders on edges spanning multiple levels.',
                usePreviewPositions=True
            )
        )

        sugiyama.barycenter()
        self._steps.append(
            self._snapshotFromSugiyama(
                sugiyama=sugiyama,
                stepIndex=4,
                phaseName='barycenter',
                description='Reordered nodes within levels via barycenter sweeps to minimize edge crossings.',
                usePreviewPositions=True
            )
        )

        sugiyama.addNonHierarchicalNodes()
        sugiyama.assignCoordinates()
        self._steps.append(
            self._snapshotFromSugiyama(
                sugiyama=sugiyama,
                stepIndex=5,
                phaseName='assignCoordinates',
                description='Placed non-hierarchical nodes, balanced coordinates, and computed link control points.',
                usePreviewPositions=False
            )
        )

    def _snapshotInitial(self, stepIndex: int) -> SugiyamaStepSnapshot:
        """
        Create the initial unlaid snapshot directly from the preset dataset.

        Args:
            stepIndex: Step sequence index.

        Returns:
            Initial SugiyamaStepSnapshot.
        """
        unleveled: List[SugiyamaNodeSnapshot] = []
        nodeSpec:  SugiyamaNodeSpec
        for nodeSpec in self._dataSet.nodes:
            unleveled.append(
                SugiyamaNodeSnapshot(
                    name=nodeSpec.name,
                    isVirtual=False,
                    level=-1,
                    index=-1,
                    barycenter=0.0,
                    x=nodeSpec.x,
                    y=nodeSpec.y,
                    width=nodeSpec.width,
                    height=nodeSpec.height,
                )
            )

        links:    List[SugiyamaLinkSnapshot] = []
        edgeSpec: SugiyamaEdgeSpec
        for edgeSpec in self._dataSet.edges:
            isHierarchical: bool = edgeSpec.linkType == LinkType.INHERITANCE or edgeSpec.linkType == LinkType.INTERFACE
            links.append(
                SugiyamaLinkSnapshot(
                    sourceName=edgeSpec.sourceName,
                    targetName=edgeSpec.targetName,
                    linkType=edgeSpec.linkType,
                    isHierarchical=isHierarchical,
                    controlPoints=[],
                )
            )

        return SugiyamaStepSnapshot(
            stepIndex=stepIndex,
            phaseName='Initial (unlaid)',
            description=self._dataSet.description,
            levels=[],
            unleveledNodes=unleveled,
            links=links,
            crossingCount=0,
            virtualNodeCount=0,
        )

    def _snapshotFromSugiyama(
        self,
        sugiyama:            Sugiyama,
        stepIndex:           int,
        phaseName:           str,
        description:         str,
        usePreviewPositions: bool,
    ) -> SugiyamaStepSnapshot:
        """
        Capture a snapshot of the Sugiyama algorithm's current internal state.

        Args:
            sugiyama: Active Sugiyama instance.
            stepIndex: Step sequence index.
            phaseName: Name of the completed phase.
            description: Human-readable summary of the phase.
            usePreviewPositions: If True, compute level-aligned preview (x, y) coordinates.

        Returns:
            SugiyamaStepSnapshot representing the current state.
        """
        levelsData:   Levels                       = sugiyama.levels
        levelSnaps:   List[List[SugiyamaNodeSnapshot]] = []
        placedNames:  Dict[str, bool]              = {}
        virtualCount: int                          = 0
        virtualIdx:   int                          = 0

        yCoord:    int = UP_MARGIN
        levelIdx:  int = 0
        levelList: NodeList
        for levelList in levelsData:
            rowSnaps:  List[SugiyamaNodeSnapshot] = []
            xCoord:    int = LEFT_MARGIN
            maxHeight: int = 0

            node: Nodes
            for node in levelList:
                isVirtual: bool = isinstance(node, VirtualSugiyamaNode)
                if isVirtual:
                    virtualCount += 1
                    virtualIdx += 1
                    nodeName: str = f'V{virtualIdx}'
                    width:    int = VIRTUAL_NODE_DISPLAY_SIZE
                    height:   int = VIRTUAL_NODE_DISPLAY_SIZE
                else:
                    realNode: RealSugiyamaNode = cast(RealSugiyamaNode, node)
                    nodeName = realNode.name
                    width, height = realNode.size

                if usePreviewPositions:
                    posX: int = xCoord
                    posY: int = yCoord
                else:
                    posX, posY = node.position

                rawIndex: Optional[int] = node.index
                nodeIndex: int = -1
                if rawIndex is not None:
                    nodeIndex = rawIndex

                rawBarycenter: Optional[float] = node.barycenter
                barycenterVal: float = 0.0
                if rawBarycenter is not None:
                    barycenterVal = float(rawBarycenter)

                placedNames[nodeName] = True
                rowSnaps.append(
                    SugiyamaNodeSnapshot(
                        name=nodeName,
                        isVirtual=isVirtual,
                        level=levelIdx,
                        index=nodeIndex,
                        barycenter=barycenterVal,
                        x=int(posX),
                        y=int(posY),
                        width=int(width),
                        height=int(height),
                    )
                )
                xCoord += width + H_SPACE
                if height > maxHeight:
                    maxHeight = height

            levelSnaps.append(rowSnaps)
            yCoord += maxHeight + V_SPACE
            levelIdx += 1

        unleveled: List[SugiyamaNodeSnapshot] = []
        nodeSpec:  SugiyamaNodeSpec
        for nodeSpec in self._dataSet.nodes:
            if nodeSpec.name not in placedNames:
                unleveled.append(
                    SugiyamaNodeSnapshot(
                        name=nodeSpec.name,
                        isVirtual=False,
                        level=-1,
                        index=-1,
                        barycenter=0.0,
                        x=nodeSpec.x,
                        y=nodeSpec.y,
                        width=nodeSpec.width,
                        height=nodeSpec.height,
                    )
                )

        # noinspection PyProtectedMember
        sugiyamaLinks: List[SugiyamaLink] = sugiyama._sugiyamaLinksList
        linkSnaps:     List[SugiyamaLinkSnapshot] = []
        sLink:         SugiyamaLink
        for sLink in sugiyamaLinks:
            srcName: str = cast(UmlClass, sLink.umlLink.sourceShape).modelClass.name
            dstName: str = cast(UmlClass, sLink.umlLink.destinationShape).modelClass.name
            pts:     List[Tuple[int, int]] = []
            if not usePreviewPositions and phaseName == 'assignCoordinates':
                rawPts = sLink.umlLink.GetLineControlPoints()
                if rawPts is not None:
                    for pt in rawPts:
                        pts.append((int(pt.x), int(pt.y)))

            isHierarchical: bool = sLink.linkType == LinkType.INHERITANCE or sLink.linkType == LinkType.INTERFACE
            linkSnaps.append(
                SugiyamaLinkSnapshot(
                    sourceName=srcName,
                    targetName=dstName,
                    linkType=sLink.linkType,
                    isHierarchical=isHierarchical,
                    controlPoints=pts,
                )
            )

        # noinspection PyProtectedMember
        crossings: int = sugiyama._getNbIntersectAll()

        return SugiyamaStepSnapshot(
            stepIndex=stepIndex,
            phaseName=phaseName,
            description=description,
            levels=levelSnaps,
            unleveledNodes=unleveled,
            links=linkSnaps,
            crossingCount=crossings,
            virtualNodeCount=virtualCount,
        )
