

from abc import ABC
from abc import abstractmethod

from typing import NewType
from typing import Optional
from typing import Tuple
from typing import List
from typing import TYPE_CHECKING
from umlextensions.tools.sugiyama.SugiyamaPreferences import SugiyamaPreferences

if TYPE_CHECKING:
    from umlextensions.tools.sugiyama.SugiyamaLink import SugiyamaLink

SugiyamaVertexEdge   = NewType("SugiyamaVertexEdge",  Tuple['SugiyamaNode', 'SugiyamaLink'])
SugiyamaVertexEdges  = NewType("SugiyamaVertexEdges", List[SugiyamaVertexEdge])
OptionalSugiyamaNode = Optional['SugiyamaNode']

BALANCE_MOVE_THRESHOLD: int = 3
UNASSIGNED_INDEX:       int = -1
UNASSIGNED_LEVEL:       int = -1


class SugiyamaNode(ABC):
    """
    Real or virtual Sugiyama node interface.

    This class is an interface, you should not have an object of type
    SugiyamaNode. You have to use RealSugiyamaNode or VirtualSugiyamaNode
    objects.
    """
    def __init__(self, horizontalSpacing: Optional[int] = None):
        """
        Initialize Sugiyama node level, index, neighbor, and link state.

        Args:
            horizontalSpacing: Optional minimum horizontal clearance buffer. If omitted,
                               defaults to SugiyamaPreferences().horizontalSpacing.
        """
        self._barycenter: Optional[int]        = None
        self._index:      int                  = UNASSIGNED_INDEX
        self._level:      int                  = UNASSIGNED_LEVEL
        self._leftNode:   OptionalSugiyamaNode = None
        self._rightNode:  OptionalSugiyamaNode = None
        self._parents:    SugiyamaVertexEdges  = SugiyamaVertexEdges([])
        self._children:   SugiyamaVertexEdges  = SugiyamaVertexEdges([])
        self._links:      SugiyamaVertexEdges  = SugiyamaVertexEdges([])

        if horizontalSpacing is None:
            self._horizontalSpacing: int = SugiyamaPreferences().horizontalSpacing
        else:
            self._horizontalSpacing = horizontalSpacing

    @property
    @abstractmethod
    def size(self) -> Tuple[int, int]:
        """
        Get the size of the node.

        Returns:    (int, int): tuple (width, height)
        """
        pass

    @property
    @abstractmethod
    def position(self) -> Tuple[int, int]:
        """
        Get position of node.

        Returns:    (int, int): tuple (x, y) in absolute coordinates
        """
        pass

    @position.setter
    @abstractmethod
    def position(self, pos: Tuple[int, int]):
        """
        Set position of node.

        Args:
            pos: (x, y) position in absolute coordinates
        """
        pass

    def addParent(self, parent: 'SugiyamaNode', link: 'SugiyamaLink'):
        """
        Update parent list

        Args:
            parent:  The parent
            link:   Link between self and parent
        """
        sugiyamaData: SugiyamaVertexEdge = SugiyamaVertexEdge((parent, link))
        self._parents.append(sugiyamaData)

    @property
    def parents(self) -> SugiyamaVertexEdges:
        """
        List of parent nodes connected via hierarchical links (Inheritance or Realization).

        Returns:
            List of (SugiyamaNode, SugiyamaLink) tuples for this node's parents.
        """
        return self._parents

    @property
    def children(self) -> SugiyamaVertexEdges:
        """
        List of child nodes derived from this node via hierarchical links (Inheritance or Realization).

        Returns:
            List of (SugiyamaNode, SugiyamaLink) tuples for this node's children.
        """
        return self._children

    @property
    def nonHierarchicalLinks(self) -> SugiyamaVertexEdges:
        """
        List of non-hierarchical links (not a parent or child relationship).

        Returns:
            List of (SugiyamaNode, SugiyamaLink) tuples.
        """
        return self._links

    @property
    def level(self) -> int:
        """
        Index of the hierarchical level containing this node.

        Returns:
            Level index.
        """
        return self._level

    @level.setter
    def level(self, level: int):
        """
        Set level index.

        Args:
            level:   level index
        """
        self._level = level

    @property
    def index(self) -> int:
        """
        Index position of this node on its level.

        Returns:
            Index of node within its level.
        """
        return self._index

    @index.setter
    def index(self, index: int):
        """
        Set index of node in level.

        Args:
            index: index of node
        """
        self._index = index

    @property
    def leftNode(self) -> OptionalSugiyamaNode:
        """
        Node directly to the left on the same level.

        Returns:
            Left neighbor node, or None if leftmost.
        """
        return self._leftNode

    @leftNode.setter
    def leftNode(self, node: OptionalSugiyamaNode):
        """
        Set the left neighbor node.

        Args:
            node:   left neighbor
        """
        self._leftNode = node

    @property
    def rightNode(self) -> OptionalSugiyamaNode:
        """
        Node directly to the right on the same level.

        Returns:
            Right neighbor node, or None if rightmost.
        """
        return self._rightNode

    @rightNode.setter
    def rightNode(self, node: OptionalSugiyamaNode):
        """
        Set the right neighbor node.

        This method must be used before balancing the graph.

        Args:
            node: right neighbor
        """
        self._rightNode = node

    @property
    def barycenter(self) -> Optional[int]:
        """
        Current pre-computed barycenter value of the node (computed from
        neighbor indexes or x coordinates).

        The barycenter value is computed when you call one of the following
        function:
            - upBarycenterIndex()
            - downBarycenterIndex()
            - upBarycenterX()
            - downBarycenterX()
        If you want to update the value, you have to recall one of the
        computing functions.

        Example:
            If you want the down barycenter computed on indexes:
            First call function downBarycenterIndex()
            and then read the barycenter property.

        Returns:   float: barycenter value
        """
        return self._barycenter

    def balance(self) -> bool:
        """
        Compute a new x coordinate for balancing the hierarchical graph.

        Evaluate the ideal x coordinate from parents and children. If it lies
        to the right of the current position, push right-hand neighbors if
        needed and update this node's position.

        Side Effects:
            Mutates ``self.position`` and may recursively shift right-hand
            neighbors' ``position`` values via ``__pushToRight()``.

        Returns:
            True if the node moved right by more than BALANCE_MOVE_THRESHOLD pixels.
        """
        # Get coordinate of node
        (x, y) = self.position

        # Evaluate best x coordinate of node
        (wantedXPos, nbFathersAndSons) = self.__computeWantedXPos()

        # If there are no parents nor sons
        if wantedXPos is None:
            # Don't move
            return False

        # If best x coord is righter than current x coordinate
        if wantedXPos > x:

            # If there is a right neighbor
            if self._rightNode is not None:
                # Check max x coord according to right neighbor
                xMax = self.getXMax()

                # If right node is to close, try to push it
                if wantedXPos > xMax:
                    self._rightNode.__pushToRight(
                        (wantedXPos - xMax) * nbFathersAndSons,
                        nbFathersAndSons)

                # Fix new position
                self.position = (min(wantedXPos, self.getXMax()), y)
            else:
                # There is no right node, fix position
                self.position = (wantedXPos, y)

        # Ignore tiny shifts (<= BALANCE_MOVE_THRESHOLD px) so balancing converges
        return self.position[0] - x > BALANCE_MOVE_THRESHOLD

    def barycenterIndex(self):
        """
        Compute the average of parents down-barycenter and sons up-barycenter.

        Before calling this function, you have to call downBarycenterIndex
        on each parent and upBarycenterIndex on each child.

        For reading this value, use getBarycenter()

        @author Nicolas Dubois
        """
        nodeList = self._parents + self._children
        if len(nodeList) == 0:
            # ~ print self.__index, "none"
            self._barycenter = None
        else:
            summation = 0
            for (node, link) in nodeList:
                if node.barycenter is not None:
                    summation += node.barycenter
            # ~ print self.__index, float(sum) / len(nodeList)
            self._barycenter = summation // len(nodeList)

    def upBarycenterX(self):
        """
        Compute the up barycenter value with fathers x coord.

        For reading this value, use getBarycenter()
        """
        self._barycenter = self.__getAverageX(self._parents)

    def downBarycenterX(self):
        """
        Compute the down barycenter value with sons x coord.

        For reading this value, use getBarycenter()
        """
        self._barycenter = self.__getAverageX(self._children)

    def barycenterX(self):
        """
        Compute the average of up and down barycenter on x coordinates.

        For reading this value, use getBarycenter()
        """
        parentsAndChildren: SugiyamaVertexEdges = SugiyamaVertexEdges(self._parents + self._children)
        self._barycenter = self.__getAverageX(parentsAndChildren)

    def getXMax(self) -> int:
        """
        Get bigger value of x coordinate according to right neighbor position.

        If there is no right neighbor, return None.

        Returns:    max x coordinate
        """
        if self._rightNode is None:
            return 0
        else:
            xRightNode = self._rightNode.position[0]
            widthSelfNode = self.size[0]
            return xRightNode - widthSelfNode - self._horizontalSpacing

    def addChild(self, child: 'SugiyamaNode', link: 'SugiyamaLink'):
        """
        Add a child.

        Args:
            child:  The child
            link:   Its Link
        """
        sugiyamaData: SugiyamaVertexEdge = SugiyamaVertexEdge((child, link))
        self._children.append(sugiyamaData)

    def addNonHierarchicalLink(self, node: 'SugiyamaNode', link: 'SugiyamaLink'):
        """
        Add a non-hierarchical link, ie not a parent or child relation.

        Args:
            node:   linked node
            link:   link between the two nodes
        """
        vertexEdge: SugiyamaVertexEdge = SugiyamaVertexEdge((node, link))
        self._links.append(vertexEdge)

    def upBarycenterIndex(self):
        """
        Compute the up barycenter value with fathers indexes.

        For reading this value, use getBarycenter()

        """
        self._barycenter = self.__getAverageIndex(self._parents)

    def downBarycenterIndex(self):
        """
        Compute the down barycenter value with sons indexes.

        For reading this value, use getBarycenter()

        """
        self._barycenter = self.__getAverageIndex(self._children)

    def fixAnchorPos(self):
        """
        Fix the positions of the anchor points.

        This function has to be overloaded.

        """
        pass

    def __getAverageIndex(self, nodeList: SugiyamaVertexEdges) -> Optional[int]:
        """
        Compute the average of indices position on all the given nodes.

        Args:
            nodeList:    [SugiyamaNode, ...] : list of nodes

        Returns:  None if nodeList is empty.  float or None : Average of indexes position
        """
        if len(nodeList) == 0:
            return None
        else:
            summation = 0
            for (node, link) in nodeList:
                summation += node.index
            return summation // len(nodeList)

    def __getAverageX(self, nodeList: SugiyamaVertexEdges) -> Optional[int]:
        """
        Compute the average of x coordinates on all the given nodes.

        Args:
            nodeList:   [(SugiyamaNode, SugiyamaLink), ...] nodeList : parents or children

        Returns:    float or None : average of x coordinates
                    None if nodeList is empty.
        """
        if len(nodeList) == 0:
            return None
        else:
            summation: int = 0
            for (node, link) in nodeList:
                summation += node.position[0] + node.size[0] // 2
            return summation // len(nodeList) - self.size[0] // 2

    def __computeWantedXPos(self):
        """
        Compute average of parents and children x coordinates.

        Returns:    tuple (int, int) : (x average, number of parents and children)
        """
        # Create list of parents and children
        parentsAndChildren = self.parents + self.children
        nbParentsAndChildren = len(parentsAndChildren)

        # If there are no parents and children
        if nbParentsAndChildren == 0:
            return None, 0

        # Compute average of parents and children x coordinates
        summation = 0
        # For all his parents and children
        for (node, link) in parentsAndChildren:
            # Get horizontal center coordinate of the node
            xCenterNode = node.position[0] + node.size[0] // 2
            summation += xCenterNode

        return summation // nbParentsAndChildren - self.size[0] // 2, nbParentsAndChildren

    def __pushToRight(self, xDeltaSum: int, nbLinks: int):
        """
        Called by the left neighbor, that function tries to push the node to
        the right for the balancing. If there is not enough space, try to
        push the next node.

        xDelta is the ideal delta on x coordinate for reaching the best balance.

        Args:
            xDeltaSum:  is xDelta multiplied by the number of parents and sons
                which are pushing to the right.

            nbLinks:   is the number of parents and sons who push from the left.
        """
        # Get current position
        (x, y) = self.position
        # Get wanted x coordinate
        (wantedXPos, nbFathersAndSons) = self.__computeWantedXPos()

        # If the node has a barycenter value (has parents or sons)
        if wantedXPos is not None:
            # Add current delta in average
            xDeltaSum += (wantedXPos - x) * nbFathersAndSons
            # Update number of fathers and sons who are pushing
            nbLinks += nbFathersAndSons
        xDelta = xDeltaSum // nbLinks

        # If the node has to be moved to the right
        if xDelta > 0:
            # If the node has a right neighbor
            if self._rightNode is not None:
                xMax = self.getXMax()
                # If we need more place, try to push the right neighbor
                if xMax < x + xDelta:
                    self._rightNode.__pushToRight(
                        (x + xDelta - xMax) * nbLinks, nbLinks)
                # Fix the new position
                self.position = (min(x + xDelta, self.getXMax()), y)
            else:
                # No right neighbor, fix the new position
                self.position = (x + xDelta, y)
