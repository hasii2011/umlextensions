from typing import Dict
from typing import List
from typing import NewType
from typing import Optional
from typing import Set
from typing import Union

from umlshapes.links.UmlLink import UmlLink
from umlshapes.ShapeTypes import UmlShape
from umlshapes.ShapeTypes import UmlShapes
from umlshapes.frames.UmlFrame import UmlFrame
from umlshapes.shapes.UmlClass import UmlClass
from umlshapes.shapes.UmlNote import UmlNote
from umlshapes.links.UmlInheritance import UmlInheritance
from umlshapes.links.UmlInterface import UmlInterface

from umlextensions.tools.sugiyama.SugiyamaLink import SugiyamaLink
from umlextensions.tools.sugiyama.RealSugiyamaNode import RealSugiyamaNode
from umlextensions.tools.sugiyama.VirtualSugiyamaNode import VirtualSugiyamaNode

HierarchicalGraphNode     = Union[RealSugiyamaNode, VirtualSugiyamaNode]
HierarchicalGraphNodes    = NewType('HierarchicalGraphNodes', List[HierarchicalGraphNode])
NonHierarchicalGraphNodes = NewType('NonHierarchicalGraphNodes', List[RealSugiyamaNode])
NonHierarchicalGraphLinks = NewType('NonHierarchicalGraphLinks', List[SugiyamaLink])


class SugiyamaGraphBuilder:
    """
    Constructs the Sugiyama layout graph from canvas UML shapes.

    Translates UML diagram shapes (classes, notes, and links) into the internal
    Sugiyama representation: RealSugiyamaNode instances and SugiyamaLink instances,
    classifying links as hierarchical (inheritance, interface) or non-hierarchical
    (associations), and partitioning nodes accordingly.
    """

    def __init__(self, umlShapes: UmlShapes, umlFrame: UmlFrame, horizontalSpacing: Optional[int] = None):
        """
        Initialize the graph builder.

        Args:
            umlShapes:         The list of UML shapes on the diagram canvas.
            umlFrame:          The UML diagram frame owning the shapes and links.
            horizontalSpacing: Optional minimum horizontal clearance buffer for nodes.
        """
        self._umlShapes:         UmlShapes     = umlShapes
        self._umlFrame:          UmlFrame      = umlFrame
        self._horizontalSpacing: Optional[int] = horizontalSpacing

        self._shapeNodeMap: Dict[UmlShape, RealSugiyamaNode] = {}
        self._hierarchicalNodeSet: Set[RealSugiyamaNode] = set()

        self._realNodes: List[RealSugiyamaNode] = []
        self._links: List[SugiyamaLink] = []
        self._hierarchicalNodes: HierarchicalGraphNodes = HierarchicalGraphNodes([])
        self._nonHierarchicalNodes: NonHierarchicalGraphNodes = NonHierarchicalGraphNodes([])
        self._nonHierarchicalLinks: NonHierarchicalGraphLinks = NonHierarchicalGraphLinks([])

    @property
    def realNodes(self) -> List[RealSugiyamaNode]:
        """
        Get all real nodes created from diagram shapes.

        Returns:
            List of RealSugiyamaNode.
        """
        return self._realNodes

    @property
    def links(self) -> List[SugiyamaLink]:
        """
        Get all Sugiyama links created from diagram relations.

        Returns:
            List of SugiyamaLink.
        """
        return self._links

    @property
    def hierarchicalNodes(self) -> HierarchicalGraphNodes:
        """
        Get nodes participating in the hierarchical graph.

        Returns:
            HierarchicalGraphNodes list of RealSugiyamaNode.
        """
        return self._hierarchicalNodes

    @property
    def nonHierarchicalNodes(self) -> NonHierarchicalGraphNodes:
        """
        Get nodes not participating in any hierarchical relationship.

        Returns:
            NonHierarchicalGraphNodes list of RealSugiyamaNode.
        """
        return self._nonHierarchicalNodes

    @property
    def nonHierarchicalLinks(self) -> NonHierarchicalGraphLinks:
        """
        Get non-hierarchical links between nodes.

        Returns:
            NonHierarchicalGraphLinks list of SugiyamaLink.
        """
        return self._nonHierarchicalLinks

    @classmethod
    def build(cls, umlShapes: UmlShapes, umlFrame: UmlFrame, horizontalSpacing: Optional[int] = None) -> 'SugiyamaGraphBuilder':
        """
        Factory method to construct and execute a SugiyamaGraphBuilder.

        Args:
            umlShapes:         The list of UML shapes on the diagram canvas.
            umlFrame:          The UML diagram frame owning the shapes and links.
            horizontalSpacing: Optional minimum horizontal clearance buffer for nodes.

        Returns:
            Constructed SugiyamaGraphBuilder instance with populated graph collections.
        """
        builder: SugiyamaGraphBuilder = cls(umlShapes=umlShapes, umlFrame=umlFrame, horizontalSpacing=horizontalSpacing)
        builder.execute()
        return builder

    def execute(self):
        """
        Execute the graph construction lifecycle.
        """
        for umlShape in self._umlShapes:
            if isinstance(umlShape, UmlClass) or isinstance(umlShape, UmlNote):
                self._getOrCreateNode(umlShape)
            elif isinstance(umlShape, UmlLink):
                self._processLink(umlShape)

        self._collectNonHierarchicalNodes()

    def _getOrCreateNode(self, shape: UmlShape) -> RealSugiyamaNode:
        """
        Retrieve the existing RealSugiyamaNode for a shape or create and register a new one.

        Args:
            shape: The UML shape (e.g. UmlClass or UmlNote).

        Returns:
            The corresponding RealSugiyamaNode.
        """
        if shape not in self._shapeNodeMap:
            node: RealSugiyamaNode = RealSugiyamaNode(umlShape=shape, horizontalSpacing=self._horizontalSpacing)
            self._realNodes.append(node)
            self._shapeNodeMap[shape] = node

        return self._shapeNodeMap[shape]

    def _processLink(self, linkShape: UmlLink):
        """
        Process a link shape, creating its endpoints and classifying the relation.

        Args:
            linkShape: The UML link shape from the canvas.
        """
        srcShape: UmlShape = linkShape.sourceShape
        dstShape: UmlShape = linkShape.destinationShape

        srcNode: RealSugiyamaNode = self._getOrCreateNode(srcShape)
        dstNode: RealSugiyamaNode = self._getOrCreateNode(dstShape)

        link: SugiyamaLink = SugiyamaLink(umlLink=linkShape, umlFrame=self._umlFrame)
        self._links.append(link)

        link.source      = srcNode
        link.destination = dstNode

        if isinstance(linkShape, UmlInheritance) or isinstance(linkShape, UmlInterface):
            self._addHierarchicalRelation(srcNode=srcNode, dstNode=dstNode, link=link)
        else:
            self._addNonHierarchicalRelation(srcNode=srcNode, dstNode=dstNode, link=link)

    def _addHierarchicalRelation(
        self,
        srcNode: RealSugiyamaNode,
        dstNode: RealSugiyamaNode,
        link: SugiyamaLink,
    ):
        """
        Wire parent/child relationships for a hierarchical link and track in hierarchy.

        Args:
            srcNode: The source RealSugiyamaNode (the subtype/implementer).
            dstNode: The destination RealSugiyamaNode (the supertype/interface).
            link:    The hierarchical SugiyamaLink connecting them.
        """
        srcNode.addParent(dstNode, link)
        dstNode.addChild(srcNode, link)

        self._recordHierarchicalNode(srcNode)
        self._recordHierarchicalNode(dstNode)

    def _recordHierarchicalNode(self, node: RealSugiyamaNode):
        """
        Record a node in the hierarchical graph nodes list if not already present.

        Args:
            node: The RealSugiyamaNode taking part in the hierarchy.
        """
        if node not in self._hierarchicalNodeSet:
            self._hierarchicalNodeSet.add(node)
            self._hierarchicalNodes.append(node)

    def _addNonHierarchicalRelation(
        self,
        srcNode: RealSugiyamaNode,
        dstNode: RealSugiyamaNode,
        link: SugiyamaLink,
    ):
        """
        Wire neighbor relations for a non-hierarchical link and track in non-hierarchical links.

        Args:
            srcNode: The source RealSugiyamaNode.
            dstNode: The destination RealSugiyamaNode.
            link:    The non-hierarchical SugiyamaLink connecting them.
        """
        srcNode.addNonHierarchicalLink(dstNode, link)
        dstNode.addNonHierarchicalLink(srcNode, link)
        self._nonHierarchicalLinks.append(link)

    def _collectNonHierarchicalNodes(self):
        """
        Collect all nodes that do not participate in the hierarchy.
        """
        for sugiyamaNode in self._shapeNodeMap.values():
            if sugiyamaNode not in self._hierarchicalNodeSet:
                self._nonHierarchicalNodes.append(sugiyamaNode)
