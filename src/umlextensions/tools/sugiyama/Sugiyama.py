
from typing import Dict
from typing import List
from typing import NewType
from typing import Tuple
from typing import cast

from logging import Logger
from logging import getLogger

from copy import copy

from umlmodel.enumerations.LinkType import LinkType
from umlshapes.ShapeTypes import UmlShapes
from umlshapes.frames.UmlFrame import UmlFrame

from umlextensions.ExtensionsPreferences import ExtensionsPreferences

from umlextensions.IExtensionsFacade import IExtensionsFacade

from umlextensions.tools.sugiyama.SugiyamaLink import SugiyamaLink

from umlextensions.tools.sugiyama.SugiyamaConstants import H_SPACE
from umlextensions.tools.sugiyama.SugiyamaConstants import LEFT_MARGIN
from umlextensions.tools.sugiyama.SugiyamaConstants import UP_MARGIN
from umlextensions.tools.sugiyama.SugiyamaConstants import V_SPACE

from umlextensions.tools.sugiyama.SugiyamaGlobals import SugiyamaGlobals

from umlextensions.tools.sugiyama.RealSugiyamaNode import RealSugiyamaNode
from umlextensions.tools.sugiyama.VirtualNodeInserter import Levels
from umlextensions.tools.sugiyama.VirtualNodeInserter import NodeList
from umlextensions.tools.sugiyama.VirtualNodeInserter import Nodes
from umlextensions.tools.sugiyama.VirtualNodeInserter import VirtualNodeInserter

from umlextensions.tools.sugiyama.SugiyamaGraphBuilder import HierarchicalGraphNodes
from umlextensions.tools.sugiyama.SugiyamaGraphBuilder import NonHierarchicalGraphNodes
from umlextensions.tools.sugiyama.SugiyamaGraphBuilder import NonHierarchicalGraphLinks
from umlextensions.tools.sugiyama.SugiyamaGraphBuilder import SugiyamaGraphBuilder

NodeIndices = NewType('NodeIndices', List[int])


class Sugiyama:
    """
    Automatic layout algorithm based on Sugiyama levels.

    This algorithm will change the class and links positions (not the
    structure). This plugin gives good result with diagrams that contain
    a lot of hierarchical relations (inheritance and interface), and poor
    association relations.

    """

    def __init__(self, umlFrame: UmlFrame, extensionsFacade: IExtensionsFacade):

        self.logger: Logger = getLogger(__name__)

        self._extensionsFacade: IExtensionsFacade     = extensionsFacade
        self._umlFrame:         UmlFrame              = umlFrame
        self._preferences:      ExtensionsPreferences = ExtensionsPreferences()

        self._realSugiyamaNodesList: List[RealSugiyamaNode] = []
        """
        List of all RealSugiyamaNodes created from diagram shapes.
        """
        self._sugiyamaLinksList: List[SugiyamaLink] = []
        """
        List of all SugiyamaLinks created from diagram relations.
        """

        self._hierarchyGraphNodesList: HierarchicalGraphNodes = HierarchicalGraphNodes([])
        """
        List of Real and Virtual Sugiyama nodes that take part in the hierarchy.
        """

        self._nonHierarchyGraphNodesList: NonHierarchicalGraphNodes = NonHierarchicalGraphNodes([])
        """
        List of Sugiyama nodes that are not in a hierarchy.
        """
        self._nonHierarchyGraphLinksList: NonHierarchicalGraphLinks = NonHierarchicalGraphLinks([])
        """
        List of non-hierarchical links between nodes.
        """

        self._levels: Levels = Levels([])
        """
        Ordered list of levels; each level contains real and virtual nodes.
        """

    @property
    def levels(self) -> Levels:
        """
        For testability and security you only get a copy

        Returns:  Internal levels structure
        """
        levels: Levels = copy(self._levels)
        return levels

    def buildGraph(self, umlShapes: UmlShapes):
        """
        Build the internal layout graph representation from canvas UML shapes.

        A RealSugiyamaNode is created for each class and note, and a SugiyamaLink
        is created for each relation, classifying them as hierarchical or
        non-hierarchical.

        Args:
            umlShapes: The UML shapes on the diagram canvas.
        """
        builder: SugiyamaGraphBuilder = SugiyamaGraphBuilder.build(
            umlShapes=umlShapes,
            umlFrame=self._umlFrame,
        )

        self._realSugiyamaNodesList      = builder.realNodes
        self._sugiyamaLinksList          = builder.links
        self._hierarchyGraphNodesList    = builder.hierarchicalNodes
        self._nonHierarchyGraphNodesList = builder.nonHierarchicalNodes
        self._nonHierarchyGraphLinksList = builder.nonHierarchicalLinks

    def levelFind(self) -> bool:
        """
        Compute the best hierarchical level for each node.

        Returns: `True` if we computed the best, else `False` if there is a
        cycle in hierarchical links
        """
        hierarchicalGraphNodes: HierarchicalGraphNodes = self._hierarchyGraphNodesList
        # Fix nodes indexes corresponding to matrix column and line index
        nbNodes = len(hierarchicalGraphNodes)  # Number of nodes in hierarchy
        for i in range(nbNodes):
            hierarchicalGraphNodes[i].index = i
        # Initialize the boolean matrix
        #
        # Example of use:
        #
        #      |A|B|C
        #     -+-+-+-
        #     A|0|0|1 <-- that 1 means A is C's father
        #     -+-+-+-     and is on coordinates matrix[2][0]
        #     B|0|0|0
        #     -+-+-+-     matrix[column][line]
        #     C|0|1|0
        #
        #
        # noinspection PyUnusedLocal
        matrix = [[0 for el in range(nbNodes)] for el2 in range(nbNodes)]
        # Fill matrix
        # For each node in graph
        for node in hierarchicalGraphNodes:
            # For each father
            for (father, link) in node.parents:
                # Mark relation with a '1' on coordinates[index Son][index Father]
                matrix[node.index][father.index] = 1
        # Define levels

        # Sum each column of the matrix
        # Old code would not pass mypy or pycharm_projects
        # sumColumns = [None for el in range(nbNodes)]
        # el not used
        # noinspection PyUnusedLocal
        sumColumns: List[int] = [0 for el in range(nbNodes)]
        for i in range(nbNodes):
            sumColumns[i] = 0
            for el in matrix[i]:
                sumColumns[i] += el

        # Index of nodes that are not in any level yet
        indexNodes: NodeIndices = NodeIndices(list(range(nbNodes)))
        # While not all nodes have an attributed level
        while indexNodes:
            level: NodeList = NodeList([])
            indexNodesNotSel: NodeIndices = NodeIndices(indexNodes[:])
            indexNodesSel: NodeIndices = NodeIndices([])

            # For all nodes that haven't an attributed level
            candidateIndex: int
            for candidateIndex in indexNodes:
                # When the sum of his matrix column is 0, that means he has no
                # parent or his parents are already in a level
                if sumColumns[candidateIndex] == 0:
                    # The node is attributed on the current level
                    # Update the lists of selected nodes
                    indexNodesSel.append(candidateIndex)
                    indexNodesNotSel.remove(candidateIndex)
            # If no nodes is selected, there is a cycle in hierarchical links
            if not indexNodesSel:
                return False

            # For all the current level's nodes
            nodeIndex: int
            for nodeIndex in indexNodesSel:
                sugiyamaNode: Nodes = hierarchicalGraphNodes[nodeIndex]
                level.append(sugiyamaNode)
                # Update the sum of the columns when we remove the line of the
                # node in the matrix
                notSelIndex: int
                for notSelIndex in indexNodesNotSel:
                    sumColumns[notSelIndex] -= matrix[notSelIndex][nodeIndex]
            # Update the list of the nodes that haven't a level yet
            indexNodes = NodeIndices(indexNodesNotSel[:])
            # Add the current level to the list
            self._levels.append(level)

        # Fix nodes index and level for each node
        for idx in range(len(self._levels)):
            level = self._levels[idx]
            for i in range(len(level)):
                node = level[i]
                node.index = i
                node.level = idx

        # No error
        return True

    def addVirtualNodes(self):
        """
        Add a virtual node by level crossed between fathers and sons that are
        separated by more than one level.
        """
        for link in self._sugiyamaLinksList:
            if link.linkType == LinkType.INHERITANCE or link.linkType == LinkType.INTERFACE:
                VirtualNodeInserter.insert(link, self._levels)

    def barycenter(self):
        """
        Find nodes index for minimizing hierarchical links crossing.
        """
        MAX_ITER = 20

        while self._getNbIntersectAll() > 0 and MAX_ITER > 0:

            # Downward phase

            # For each level except first
            for i in range(1, len(self._levels)):

                # Compute parents down-barycenter
                if i > 0:
                    self._downBarycenterLevel(i - 1)
                # Compute sons up-barycenter
                if i < len(self._levels) - 1:
                    self._upBarycenterLevel(i + 1)

                # Compute up-barycenter on current level
                self._upBarycenterLevel(i)
                self._sortLevel(i)
                self._shiftSameBarycenter(i)

            # Upward phase

            if self._getNbIntersectAll() > 0:

                indexList = list(range(len(self._levels) - 1))
                indexList.reverse()
                for i in indexList:

                    self._downBarycenterLevel(i)
                    self._sortLevel(i)
                    self._shiftSameBarycenter(i)

                MAX_ITER -= 1

    def addNonHierarchicalNodes(self):
        """
        Add non-hierarchical nodes into levels.
        """
        # Vocabulary:
        # Internal node: nodes present in levels
        # External node: nodes not present in levels yet

        # Dictionary internalNodes externalNodes:
        # Keys are internal respectively external nodes
        # Values :
        #   - externalNodes : # of links to internal nodes
        internalNodes: Dict[Nodes, None]          = {}
        externalNodes: Dict[RealSugiyamaNode, int] = {}

        # Make dictionary of internal nodes
        for node in self._hierarchyGraphNodesList:
            internalNodes[node] = None

        # Make dictionary of external nodes
        for node in self._nonHierarchyGraphNodesList:
            # Count links to internal nodes
            count = 0
            for (dstNode, link) in node.nonHierarchicalLinks:
                if dstNode in internalNodes:
                    count += 1

            # Add node to externalNodes
            externalNodes[node] = count

        # If there is no level (no inheritance or realization) but there are
        # nodes to put in, create new level
        if not self._levels and externalNodes:
            # Add one level for nodes
            self._levels.append(NodeList([]))

        # Function for getting node that has most connections to internal
        # nodes
        def mostConnection(zExternalNodes: Dict[RealSugiyamaNode, int]) -> RealSugiyamaNode:

            maxNode:    RealSugiyamaNode = cast(RealSugiyamaNode, cast(object, None))
            maxNbLinks: int              = -1
            for (nbLinkNode, nbLinks) in list(zExternalNodes.items()):
                # If current node has more connections
                if nbLinks > maxNbLinks:
                    maxNode    = nbLinkNode
                    maxNbLinks = nbLinks

            return maxNode
        # Function for evaluating best level and best index for an external
        # node

        def bestPos(
            zExtNode:       RealSugiyamaNode,
            zInternalNodes: Dict[Nodes, None],
        ) -> Tuple[int | None, int | None]:
            """
            Evaluate average of level of linked nodes
            Args:
                zExtNode:
                zInternalNodes:

            Returns: (level, index)
            """
            nb:        int = 0
            summation: int = 0
            nodes     = []  # List of connected internal nodes

            # For all non-hierarchical links
            for (zDstNode, innerLink) in zExtNode.nonHierarchicalLinks:
                # If node linked to internal nodes
                if zDstNode in zInternalNodes:
                    # Add connected node to list
                    nodes.append(zDstNode)
                    # Add level to sum and count number of links
                    summation += zDstNode.level
                    nb += 1
            # If no links to internal nodes
            # if nodes == []:
            if not nodes:
                return None, None

            # Find closer node to average position
            avgLevel = summation // nb
            levelNodes = []  # List of nodes on same level
            bestLevel = None
            # Fix best level on first node
            if nodes:
                bestLevel = nodes[0].level

            # For all connected internal nodes
            for connectedInternalNode in nodes:
                nodeLevel = connectedInternalNode.level

                # If current node is on bestLevel
                if nodeLevel == bestLevel:
                    levelNodes.append(connectedInternalNode)

                # Else if current node is nearer to average position or
                # is at same distance but with less nodes on level
                # TODO Refactor this test to a method
                elif abs(nodeLevel - avgLevel) < abs(bestLevel - avgLevel) or (abs(nodeLevel - avgLevel) == abs(bestLevel - avgLevel) and       # type: ignore
                                                                               len(self._levels[nodeLevel]) < len(self._levels[bestLevel])):    # type: ignore

                    # Store best level
                    bestLevel = nodeLevel

                    # Start new list of nodes on new best level
                    levelNodes = [connectedInternalNode]

            # Return average of nodes' level
            return bestLevel, levelNodes[len(levelNodes) // 2].index

        # Function for getting level that has fewer nodes.
        def getLessFilledLevel():

            lessLevel = 0  # Index of level that has less node in it
            nb = len(self._levels[lessLevel])

            for x in range(1, len(self._levels)):
                if len(self._levels[x]) < nb:
                    lessLevel = x
                    nb = len(self._levels[x])

            return lessLevel

        # Function to move a node from internal to external nodes.
        def moveExternal2Internal(
            zNode:          RealSugiyamaNode,
            zInternalNodes: Dict[Nodes, None],
            zExternalNodes: Dict[RealSugiyamaNode, int],
        ):

            # Remove node from external nodes
            del zExternalNodes[zNode]

            # Add node to internal nodes
            zInternalNodes[zNode] = None

            # For all his linked external nodes, update their counter
            # zExtNode = None   NOT USED
            for (zDstNode, innerLink) in zNode.nonHierarchicalLinks:
                if isinstance(zDstNode, RealSugiyamaNode) and zDstNode in zExternalNodes:
                    zExternalNodes[zDstNode] += 1

        # While there are nodes still not in hierarchy
        while externalNodes:
            # Get external node that has most connections to internalNodes
            extNode: RealSugiyamaNode = mostConnection(externalNodes)

            self.logger.info(f'extNode.name: `{extNode.name}`')
            # Evaluate best level and index for the node
            (level, index) = bestPos(extNode, internalNodes)

            # If node has no connection to internal node
            if level is None or index is None:
                # Find level that is less filled of nodes
                level = getLessFilledLevel()
                index = len(self._levels[level])

            # Add node in levels
            extNode.level = level
            extNode.index = index
            self._levels[level].insert(index, extNode)
            # Shift index attributes on right
            for i in range(index + 1, len(self._levels[level])):
                self._levels[level][i].index = i

            # Move node from external to internal nodes
            moveExternal2Internal(extNode, internalNodes, externalNodes)

    def fixPositions(self):
        """
        Compute coordinates for nodes and links.
        """
        self._fixNodesNeighbors()
        self._fixNodesPositions()
        self._fixLinksPositions()

    def _downBarycenterLevel(self, indexLevel: int):
        """
        Compute down barycenter (from sons) for all nodes on level.

        Args:
            indexLevel:   The index level
        """
        level: NodeList = self._levels[indexLevel]
        for node in level:
            node.downBarycenterIndex()

    def _upBarycenterLevel(self, indexLevel: int):
        """
        Compute up barycenter (from parents) for all nodes on level.

        @param indexLevel : index of level
        @author Nicolas Dubois
        """
        level: NodeList = self._levels[indexLevel]
        for node in level:
            node.upBarycenterIndex()

    def _shiftSameBarycenter(self, indexLevel: int):
        """
        Do a left circular shifting on nodes with same barycenter on a level.

        For each group of nodes which have the same pre-calculated value, do a
        left circular shifting of the nodes.

        @param indexLevel : index of level
        @author Nicolas Dubois
        """
        level: NodeList = self._levels[indexLevel]

        # Save current level
        levelSaved: NodeList = NodeList(level[:])
        # Count crossings
        nbIntersections: int = self._getNbIntersectAll()

        # Shift same barycenter
        for i in range(len(level) - 1):
            if level[i].barycenter is not None and level[i].barycenter == level[i + 1].barycenter:

                shiftedNode: Nodes = level.pop(i + 1)
                level.insert(i, shiftedNode)
                # Fix index
                level[i].index = i
                level[i + 1].index = i + 1

        # If new order give more intersections, return to old order
        if self._getNbIntersectAll() > nbIntersections:
            self._levels[indexLevel] = levelSaved
            for i in range(len(levelSaved)):
                levelSaved[i].index = i

    def _sortLevel(self, indexLevel: int):
        """
        Sort nodes on a level according to pre-calculated barycenter value.
        Nodes that don't have a barycenter value keep their place.

        Args:
            indexLevel:  index of level in self.__levels to sort
        """
        level:     NodeList = self._levels[indexLevel]
        levelCopy: NodeList = NodeList(level[:])

        nbIntersect: int = self._getNbIntersectAll()

        # Get list of nodes who have a barycenter value
        listIndex: NodeIndices = NodeIndices([])
        for i in range(len(levelCopy)):
            if levelCopy[i].barycenter is not None:
                listIndex.append(i)

        # Create list of nodes to sort
        listNodes: NodeList = NodeList([])
        idx: int
        for idx in listIndex:
            listNodes.append(levelCopy[idx])

        # Sort list of nodes
        listNodes.sort(key=SugiyamaGlobals.cmpBarycenter)

        # Put sorted list in levelCopy
        for i in range(len(listNodes)):
            levelCopy[listIndex[i]] = listNodes[i]

        # Fix indexes
        for i in range(len(levelCopy)):
            levelCopy[i].index = i

        # If there are more intersections than before, keep original order
        nbIntersect2: int = self._getNbIntersectAll()
        if nbIntersect < nbIntersect2:
            # Fix indexes
            for i in range(len(level)):
                level[i].index = i
        else:
            # Else set new order
            self._levels[indexLevel] = levelCopy
        # nbIntersect3 = self.__getNbIntersectAll()    NOT USED

    def _getNbIntersectAll(self) -> int:
        """

        Returns:  The number of intersections between hierarchy relations.
        """
        count: int = 0
        for i in range(len(self._levels) - 1):
            count += self._getNbIntersect2Levels(i)

        return count

    def _getNbIntersect2Levels(self, upperLevel: int) -> int:
        """
        The two levels index are [upperLevel] and [upperLevel + 1].

        Args:
            upperLevel:  index of upper level

        Returns: The intersections number of hierarchical links between two levels.
        """
        # Get nodes from the level
        nodes: NodeList = self._levels[upperLevel]

        # Count intersect
        count: int = 0

        # For each node of the layer
        for indFatherL in range(len(nodes) - 1):
            # For each son of the current node
            for (sonL, link) in nodes[indFatherL].children:

                # Check intersect with all next parents
                indFatherR = indFatherL + 1
                while indFatherR < len(nodes):
                    for (sonR, rLink) in nodes[indFatherR].children:
                        # If intersect
                        if sonL.index > sonR.index:
                            count += 1
                    indFatherR += 1

        return count

    def _fixNodesNeighbors(self):
        """
        For each node, fix his right neighbor.

        @author Nicolas Dubois
        """
        # For each node, fix his neighbors if he has, None else
        for level in self._levels:
            nbNodes = len(level)

            for i in range(nbNodes - 1):
                level[i + 1].leftNode = level[i]
                level[i].rightNode = level[i + 1]

            # For first and last nodes of the level
            level[0].leftNode = None
            level[nbNodes - 1].rightNode = None

    def _fixNodesPositions(self):

        # Compute start positions packed on left
        y: int = UP_MARGIN
        for level in self._levels:
            x:         int = LEFT_MARGIN
            maxHeight: int = 0

            for node in level:
                (width, height) = node.size
                node.position = (x, y)
                x += width + H_SPACE
                maxHeight = max(maxHeight, height)
            y += maxHeight + V_SPACE

        if self._preferences.sugiyamaStepByStep is True:
            SugiyamaGlobals.waitKey(self._extensionsFacade, optionalMessage=None)
        else:
            self.logger.info(f'.__fixNodesPositions() is complete')

        # While nodes have to be moved
        moved: bool = True
        while moved:
            moved = False
            # Compute average coordinates for each node
            for level in self._levels:
                for node in level:
                    if node.balance():
                        moved = True
                        msg: str = f'LEVEL - node: {node} {level}'
                        if self._preferences.sugiyamaStepByStep is True:
                            SugiyamaGlobals.waitKey(self._extensionsFacade, msg)
                        else:
                            self.logger.info(msg)

    def _fixLinksPositions(self):
        """
        Compute links new positions.
        """
        # For each hierarchical link, fix anchors coordinates
        for level in self._levels:
            for node in level:
                node.fixAnchorPos()

        # For each hierarchical link, add control points to pass through
        # each virtual node
        for link in self._sugiyamaLinksList:
            link.fixControlPoints()
