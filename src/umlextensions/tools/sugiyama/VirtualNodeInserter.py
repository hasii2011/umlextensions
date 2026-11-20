from typing import List
from typing import NewType
from typing import Optional
from typing import Union

from umlextensions.tools.sugiyama.SugiyamaLink import SugiyamaLink
from umlextensions.tools.sugiyama.SugiyamaNode import SugiyamaNode
from umlextensions.tools.sugiyama.SugiyamaNode import SugiyamaVertexEdge
from umlextensions.tools.sugiyama.SugiyamaNode import SugiyamaVertexEdges
from umlextensions.tools.sugiyama.RealSugiyamaNode import RealSugiyamaNode
from umlextensions.tools.sugiyama.VirtualSugiyamaNode import VirtualSugiyamaNode

Nodes    = Union[RealSugiyamaNode, VirtualSugiyamaNode]
NodeList = NewType('NodeList', List[Nodes])
Levels   = NewType('Levels', List[NodeList])


class VirtualNodeInserter:
    """
    Inserts virtual nodes on hierarchical links that span multiple levels.

    When a hierarchical link connects a source and destination separated by
    more than one level, this class creates intermediate VirtualSugiyamaNodes,
    chains them in sequence, registers them in the hierarchy levels, and attaches
    them to the link.
    """

    def __init__(self, hierarchicalLink: SugiyamaLink, levels: Levels, horizontalSpacing: Optional[int] = None):
        """
        Initialize the inserter with the hierarchical link and the hierarchy levels.

        Args:
            hierarchicalLink:  The hierarchical SugiyamaLink to split with virtual nodes.
            levels:            The hierarchy levels structure where virtual nodes are registered.
            horizontalSpacing: Optional minimum horizontal clearance buffer for virtual nodes.
        """
        self._link:              SugiyamaLink  = hierarchicalLink
        self._levels:            Levels        = levels
        self._srcNode:           SugiyamaNode  = hierarchicalLink.source
        self._dstNode:           SugiyamaNode  = hierarchicalLink.destination
        self._horizontalSpacing: Optional[int] = horizontalSpacing
        self._virtualNodes: List[VirtualSugiyamaNode] = []

    @property
    def virtualNodes(self) -> List[VirtualSugiyamaNode]:
        """
        Get the list of created virtual nodes.

        Returns:
            List of VirtualSugiyamaNode created during insertion.
        """
        return self._virtualNodes

    @classmethod
    def insert(cls, hierarchicalLink: SugiyamaLink, levels: Levels, horizontalSpacing: Optional[int] = None) -> List[VirtualSugiyamaNode]:
        """
        Insert virtual nodes on a hierarchical link spanning multiple levels.

        Args:
            hierarchicalLink:  The hierarchical SugiyamaLink to split with virtual nodes.
            levels:            The hierarchy levels structure where virtual nodes are registered.
            horizontalSpacing: Optional minimum horizontal clearance buffer for virtual nodes.

        Returns:
            List of VirtualSugiyamaNode created and registered.
        """
        inserter: VirtualNodeInserter = cls(hierarchicalLink, levels, horizontalSpacing=horizontalSpacing)
        inserter.execute()
        return inserter.virtualNodes

    def execute(self):
        """
        Execute the virtual node insertion lifecycle.
        """
        hasVirtualNodes: bool = self._createVirtualNodes()
        if not hasVirtualNodes:
            return

        self._connectVirtualChain()
        self._registerInLevels()
        self._attachToLink()

    def _createVirtualNodes(self) -> bool:
        """
        Create virtual nodes for all intermediate levels between destination and source.

        Returns:
            True if virtual nodes were created, False if nodes are on adjacent levels.
        """
        dstNodeLevel: int = self._dstNode.level
        indexLevels: List[int] = list(range(dstNodeLevel + 1, self._srcNode.level))

        if not indexLevels:
            return False

        self._virtualNodes = [VirtualSugiyamaNode(horizontalSpacing=self._horizontalSpacing) for _ in indexLevels]

        for i in range(len(self._virtualNodes)):
            virtualNode: VirtualSugiyamaNode = self._virtualNodes[i]
            virtualNode.level = dstNodeLevel + i + 1

        return True

    def _connectVirtualChain(self):
        """
        Wire parent/child relationships between adjacent virtual nodes, and
        connect the ends of the virtual chain to the real source and destination nodes.
        """
        for i in range(len(self._virtualNodes) - 1):
            self._virtualNodes[i].addChild(self._virtualNodes[i + 1], self._link)
            self._virtualNodes[i + 1].addParent(self._virtualNodes[i], self._link)

        self._virtualNodes[-1].addChild(self._srcNode, self._link)
        self._virtualNodes[0].addParent(self._dstNode, self._link)

        self.updateLink(self._dstNode.children, self._link, self._virtualNodes[0])
        self.updateLink(self._srcNode.parents, self._link, self._virtualNodes[-1])

    def _registerInLevels(self):
        """
        Register virtual nodes in their respective level rows in the hierarchy.
        """
        dstNodeLevel: int = self._dstNode.level
        for i in range(len(self._virtualNodes)):
            level: NodeList = self._levels[dstNodeLevel + i + 1]
            level.append(self._virtualNodes[i])
            level[-1].index = len(level) - 1

    def _attachToLink(self):
        """
        Attach virtual nodes to the link ordered from bottom to top.
        """
        for i in range(len(self._virtualNodes) - 1, -1, -1):
            self._link.addVirtualNode(self._virtualNodes[i])

    @staticmethod
    def updateLink(
        vertexEdges: SugiyamaVertexEdges,
        targetLink: SugiyamaLink,
        replacementNode: Nodes,
    ):
        """
        Search a vertex edge list for a target link and replace its connected node.

        When a link is split by virtual nodes, the endpoints of the original link
        must point to the nearest virtual node instead of the original connected node.
        This method finds the edge associated with targetLink in vertexEdges
        and updates its connected node to the replacement node.

        Args:
            vertexEdges: List of (node, link) edges to search (e.g. node.children or node.parents).
            targetLink: The SugiyamaLink to match.
            replacementNode: The new node (typically a VirtualSugiyamaNode) to associate with the link.
        """
        for i in range(len(vertexEdges)):

            connectedNode: SugiyamaNode
            link:          SugiyamaLink

            connectedNode, link = vertexEdges[i]
            if targetLink == link:
                vertexEdges[i] = SugiyamaVertexEdge((replacementNode, targetLink))
                break
