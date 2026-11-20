"""
Unit tests for the Sugiyama hierarchical layout algorithm.
"""

from typing import Dict
from typing import List
from typing import Tuple

from unittest import main

from wx.lib.ogl import OGLInitialize

from codeallyadvanced.ui.UnitTestBaseW import UnitTestBaseW

from umlmodel.Class import Class
from umlmodel.Link import Link
from umlmodel.enumerations.LinkType import LinkType

from umlshapes.ShapeTypes import UmlShapes
from umlshapes.ShapeTypes import umlShapesFactory
from umlshapes.frames.ClassDiagramFrame import ClassDiagramFrame
from umlshapes.links.UmlAssociation import UmlAssociation
from umlshapes.links.UmlInheritance import UmlInheritance
from umlshapes.links.UmlLink import UmlLink
from umlshapes.pubsubengine.UmlPubSubEngine import UmlPubSubEngine
from umlshapes.shapes.UmlClass import UmlClass
from umlshapes.types.UmlDimensions import UmlDimensions
from umlshapes.types.UmlPosition import UmlPosition

from umlextensions.tools.sugiyama.Sugiyama import Levels
from umlextensions.tools.sugiyama.Sugiyama import NodeList
from umlextensions.tools.sugiyama.Sugiyama import Nodes
from umlextensions.tools.sugiyama.Sugiyama import Sugiyama
from umlextensions.tools.sugiyama.RealSugiyamaNode import RealSugiyamaNode
from umlextensions.tools.sugiyama.VirtualSugiyamaNode import VirtualSugiyamaNode
from umlextensions.tools.sugiyama.SugiyamaLink import SugiyamaLink
from umlextensions.tools.sugiyama.SugiyamaNode import SugiyamaVertexEdge
from umlextensions.tools.sugiyama.SugiyamaNode import SugiyamaVertexEdges
from umlextensions.tools.sugiyama.VirtualNodeInserter import VirtualNodeInserter

from tests.extensiondemo.ExtensionsFacade import ExtensionsFacade

DEFAULT_NODE_WIDTH:  int = 120
DEFAULT_NODE_HEIGHT: int = 50


class TestSugiyama(UnitTestBaseW):
    """
    Unit tests covering Sugiyama ingestion, level assignment, virtual nodes,
    barycenter crossing reduction, non-hierarchical placement, and coordinates.
    """

    @classmethod
    def setUpClass(cls):
        """
        Initialize class-level test fixtures via UnitTestBaseW.
        """
        super().setUpClass()

    def setUp(self):
        """
        Create a fresh hidden ClassDiagramFrame and ExtensionsFacade for each test.
        """
        super().setUp()
        OGLInitialize()
        self._umlPubSubEngine: UmlPubSubEngine   = UmlPubSubEngine()
        self._diagramFrame:    ClassDiagramFrame = ClassDiagramFrame(
            parent=self._topLevelWindow,
            umlPubSubEngine=self._umlPubSubEngine,
        )
        self._diagramFrame.Hide()
        self._facade: ExtensionsFacade = ExtensionsFacade()

    def tearDown(self):
        """
        Clean up wx resources via UnitTestBaseW.
        """
        super().tearDown()

    def _buildGraph(
        self,
        nodeSpecs: List[Tuple[str, int, int]],
        edgeSpecs: List[Tuple[str, str, LinkType]],
    ) -> Tuple[UmlShapes, Dict[str, UmlClass], List[UmlLink]]:
        """
        Populate the hidden diagram with UmlClass shapes and UmlLink connections.

        Args:
            nodeSpecs: List of (name, x, y) tuples.
            edgeSpecs: List of (sourceName, targetName, linkType) tuples.

        Returns:
            Tuple of (umlShapes, umlClassesByName, umlLinks).
        """
        umlClasses: Dict[str, UmlClass] = {}
        umlShapes:  UmlShapes           = umlShapesFactory()
        umlLinks:   List[UmlLink]       = []

        name: str
        posX: int
        posY: int
        for name, posX, posY in nodeSpecs:
            modelClass: Class    = Class(name=name)
            umlClass:   UmlClass = UmlClass(
                modelClass=modelClass,
                size=UmlDimensions(width=DEFAULT_NODE_WIDTH, height=DEFAULT_NODE_HEIGHT)
            )
            umlClass.position = UmlPosition(x=posX, y=posY)
            self._diagramFrame.umlDiagram.AddShape(umlClass)
            umlClass.SetCanvas(self._diagramFrame)
            umlClasses[name] = umlClass
            umlShapes.append(umlClass)

        srcName:  str
        dstName:  str
        linkType: LinkType
        for srcName, dstName, linkType in edgeSpecs:
            srcClass: UmlClass = umlClasses[srcName]
            dstClass: UmlClass = umlClasses[dstName]
            if linkType == LinkType.INHERITANCE:
                inhLink: Link           = Link(linkType=LinkType.INHERITANCE, source=srcClass.modelClass, destination=dstClass.modelClass)
                umlInh:  UmlInheritance = UmlInheritance(link=inhLink, baseClass=dstClass, subClass=srcClass)
                umlInh.SetCanvas(self._diagramFrame)
                umlInh.MakeLineControlPoints(2)
                srcClass.addLink(umlLink=umlInh, destinationClass=dstClass)
                self._diagramFrame.umlDiagram.AddShape(umlInh)
                umlShapes.append(umlInh)
                umlLinks.append(umlInh)
            else:
                assocLink: Link           = Link(linkType=LinkType.ASSOCIATION, source=srcClass.modelClass, destination=dstClass.modelClass)
                umlAssoc:  UmlAssociation = UmlAssociation(link=assocLink)
                umlAssoc.SetCanvas(self._diagramFrame)
                umlAssoc.MakeLineControlPoints(2)
                srcClass.addLink(umlLink=umlAssoc, destinationClass=dstClass)
                self._diagramFrame.umlDiagram.AddShape(umlAssoc)
                umlShapes.append(umlAssoc)
                umlLinks.append(umlAssoc)

        return umlShapes, umlClasses, umlLinks

    def _runFullSugiyama(self, umlShapes: UmlShapes) -> Tuple[Sugiyama, bool]:
        """
        Execute all Sugiyama phases in sequence.

        Args:
            umlShapes: Shapes to lay out.

        Returns:
            Tuple of (Sugiyama instance, levelFind success flag).
        """
        sugiyama: Sugiyama = Sugiyama(umlFrame=self._diagramFrame, extensionsFacade=self._facade)
        sugiyama.buildGraph(umlShapes=umlShapes)
        ok: bool = sugiyama.levelFind()
        if not ok:
            return sugiyama, False
        sugiyama.addVirtualNodes()
        sugiyama.barycenter()
        sugiyama.addNonHierarchicalNodes()
        sugiyama.assignCoordinates()
        return sugiyama, True

    def _assertNoLevelOverlap(self, levels: Levels):
        """
        Assert that nodes within each level do not overlap horizontally and y increases by level.

        Args:
            levels: Completed Sugiyama levels.
        """
        prevLevelY: int = -1
        levelRow:   NodeList
        for levelRow in levels:
            if len(levelRow) == 0:
                continue
            rowMaxY:  int = 0
            prevEndX: int = -1
            node:     Nodes
            for node in levelRow:
                posX, posY = node.position
                width, height = node.size
                self.assertGreaterEqual(posX, 0)
                self.assertGreaterEqual(posY, 0)
                self.assertGreater(posX, prevEndX)
                if prevLevelY >= 0:
                    self.assertGreater(posY, prevLevelY)
                prevEndX = posX + width
                if posY + height > rowMaxY:
                    rowMaxY = posY + height
            prevLevelY = rowMaxY

    def _countVirtualNodes(self, levels: Levels) -> int:
        """
        Count VirtualSugiyamaNode instances across all levels.

        Args:
            levels: Sugiyama levels.

        Returns:
            Total virtual node count.
        """
        count:    int = 0
        levelRow: NodeList
        for levelRow in levels:
            node: Nodes
            for node in levelRow:
                if isinstance(node, VirtualSugiyamaNode):
                    count += 1
        return count

    def testEmptyDiagram(self):
        """
        An empty shape list should produce no levels and succeed cleanly.
        """
        umlShapes: UmlShapes = umlShapesFactory()
        sugiyama, ok = self._runFullSugiyama(umlShapes=umlShapes)
        self.assertTrue(ok)
        self.assertEqual(len(sugiyama.levels), 0)

    def testSingleIsolatedClass(self):
        """
        A single isolated class should be placed on level 0 with valid coordinates.
        """
        umlShapes, umlClasses, _ = self._buildGraph(
            nodeSpecs=[('Solo', 300, 300)],
            edgeSpecs=[],
        )
        sugiyama, ok = self._runFullSugiyama(umlShapes=umlShapes)
        self.assertTrue(ok)
        self.assertEqual(len(sugiyama.levels), 1)
        self.assertEqual(len(sugiyama.levels[0]), 1)
        self._assertNoLevelOverlap(sugiyama.levels)
        soloPos: UmlPosition = umlClasses['Solo'].position
        self.assertGreaterEqual(soloPos.x, 0)
        self.assertGreaterEqual(soloPos.y, 0)

    def testSimpleTreeLevelsAndPositions(self):
        """
        A 3-level inheritance tree should assign 3 levels, 0 virtual nodes, and 0 crossings.
        """
        umlShapes, _, _ = self._buildGraph(
            nodeSpecs=[
                ('Animal', 120, 320),
                ('Mammal', 420, 90),
                ('Bird', 60, 90),
                ('Dog', 500, 260),
                ('Cat', 260, 180),
                ('Eagle', 260, 380),
            ],
            edgeSpecs=[
                ('Mammal', 'Animal', LinkType.INHERITANCE),
                ('Bird', 'Animal', LinkType.INHERITANCE),
                ('Dog', 'Mammal', LinkType.INHERITANCE),
                ('Cat', 'Mammal', LinkType.INHERITANCE),
                ('Eagle', 'Bird', LinkType.INHERITANCE),
            ],
        )
        sugiyama, ok = self._runFullSugiyama(umlShapes=umlShapes)
        self.assertTrue(ok)
        self.assertEqual(len(sugiyama.levels), 3)
        self.assertEqual(self._countVirtualNodes(sugiyama.levels), 0)

        self.assertEqual(sugiyama._getNbIntersectAll(), 0)
        self._assertNoLevelOverlap(sugiyama.levels)

    def testDiamondCrossingReduction(self):
        """
        Barycenter sweeps should eliminate the initial crossing in a diamond hierarchy.
        """
        umlShapes, _, _ = self._buildGraph(
            nodeSpecs=[
                ('Base', 440, 360),
                ('LeftMixin', 80, 100),
                ('RightMixin', 480, 100),
                ('DiamondChild', 280, 220),
                ('ExtraLeaf', 100, 340),
            ],
            edgeSpecs=[
                ('LeftMixin', 'Base', LinkType.INHERITANCE),
                ('RightMixin', 'Base', LinkType.INHERITANCE),
                ('DiamondChild', 'LeftMixin', LinkType.INHERITANCE),
                ('DiamondChild', 'RightMixin', LinkType.INHERITANCE),
                ('ExtraLeaf', 'LeftMixin', LinkType.INHERITANCE),
            ],
        )
        sugiyama: Sugiyama = Sugiyama(umlFrame=self._diagramFrame, extensionsFacade=self._facade)
        sugiyama.buildGraph(umlShapes=umlShapes)
        self.assertTrue(sugiyama.levelFind())
        sugiyama.addVirtualNodes()

        initialCrossings: int = sugiyama._getNbIntersectAll()
        sugiyama.barycenter()

        finalCrossings: int = sugiyama._getNbIntersectAll()
        self.assertGreaterEqual(initialCrossings, 1)
        self.assertEqual(finalCrossings, 0)
        sugiyama.addNonHierarchicalNodes()
        sugiyama.assignCoordinates()
        self._assertNoLevelOverlap(sugiyama.levels)

    def testMultiLevelSpanVirtualNodesAndControlPoints(self):
        """
        Multi-level inheritance links should insert virtual nodes and generate >2 control points.
        """
        umlShapes, _, umlLinks = self._buildGraph(
            nodeSpecs=[
                ('Root', 80, 80),
                ('Layer1A', 460, 120),
                ('Layer1B', 260, 240),
                ('Layer2', 100, 340),
                ('Leaf', 480, 340),
            ],
            edgeSpecs=[
                ('Layer1A', 'Root', LinkType.INHERITANCE),
                ('Layer1B', 'Root', LinkType.INHERITANCE),
                ('Layer2', 'Layer1A', LinkType.INHERITANCE),
                ('Leaf', 'Layer2', LinkType.INHERITANCE),
                ('Leaf', 'Root', LinkType.INHERITANCE),
                ('Layer2', 'Root', LinkType.INHERITANCE),
            ],
        )
        sugiyama, ok = self._runFullSugiyama(umlShapes=umlShapes)
        self.assertTrue(ok)
        self.assertEqual(len(sugiyama.levels), 4)
        self.assertEqual(self._countVirtualNodes(sugiyama.levels), 3)

        self.assertEqual(sugiyama._getNbIntersectAll(), 0)
        self._assertNoLevelOverlap(sugiyama.levels)

        # Leaf -> Root (index 4) spans 3 levels (2 virtual nodes), so it must have >2 control points.
        leafToRootPts = umlLinks[4].GetLineControlPoints()
        self.assertGreater(len(leafToRootPts), 2)
        # Layer1A -> Root (index 0) spans 1 level, so it keeps 2 endpoints.
        singleSpanPts = umlLinks[0].GetLineControlPoints()
        self.assertEqual(len(singleSpanPts), 2)

    def testMixedHierarchyAndNonHierarchicalNodes(self):
        """
        Association-only nodes should be placed into levels during addNonHierarchicalNodes.
        """
        umlShapes, _, _ = self._buildGraph(
            nodeSpecs=[
                ('AbstractHandler', 100, 300),
                ('HttpHandler', 440, 100),
                ('WsHandler', 280, 100),
                ('Router', 520, 300),
                ('Logger', 100, 100),
            ],
            edgeSpecs=[
                ('HttpHandler', 'AbstractHandler', LinkType.INHERITANCE),
                ('WsHandler', 'AbstractHandler', LinkType.INHERITANCE),
                ('Router', 'HttpHandler', LinkType.ASSOCIATION),
                ('Router', 'WsHandler', LinkType.ASSOCIATION),
                ('AbstractHandler', 'Logger', LinkType.ASSOCIATION),
            ],
        )
        sugiyama: Sugiyama = Sugiyama(umlFrame=self._diagramFrame, extensionsFacade=self._facade)
        sugiyama.buildGraph(umlShapes=umlShapes)
        self.assertTrue(sugiyama.levelFind())
        sugiyama.addVirtualNodes()
        sugiyama.barycenter()
        totalBefore: int = sum(len(row) for row in sugiyama.levels)
        self.assertEqual(totalBefore, 3)

        sugiyama.addNonHierarchicalNodes()
        totalAfter: int = sum(len(row) for row in sugiyama.levels)
        self.assertEqual(totalAfter, 5)

        sugiyama.assignCoordinates()
        self._assertNoLevelOverlap(sugiyama.levels)

    def testCycleDetectionReturnsFalse(self):
        """
        A cycle in hierarchical links should cause levelFind to return False.
        """
        umlShapes, _, _ = self._buildGraph(
            nodeSpecs=[
                ('ClassA', 100, 100),
                ('ClassB', 300, 100),
            ],
            edgeSpecs=[
                ('ClassA', 'ClassB', LinkType.INHERITANCE),
                ('ClassB', 'ClassA', LinkType.INHERITANCE),
            ],
        )
        sugiyama: Sugiyama = Sugiyama(umlFrame=self._diagramFrame, extensionsFacade=self._facade)
        sugiyama.buildGraph(umlShapes=umlShapes)
        self.assertFalse(sugiyama.levelFind())

    def testUpdateLinkMatchesAndReplacesNode(self):
        """
        _updateLink should replace the node matching the target link while preserving other edges.
        """
        umlShapes, umlClasses, umlLinks = self._buildGraph(
            nodeSpecs=[
                ('SourceClass', 100, 100),
                ('DestClassA', 300, 100),
                ('DestClassB', 500, 100),
            ],
            edgeSpecs=[
                ('SourceClass', 'DestClassA', LinkType.INHERITANCE),
                ('SourceClass', 'DestClassB', LinkType.INHERITANCE),
            ],
        )
        sugiyama: Sugiyama = Sugiyama(umlFrame=self._diagramFrame, extensionsFacade=self._facade)
        sugiyama.buildGraph(umlShapes=umlShapes)

        nodeA: RealSugiyamaNode = RealSugiyamaNode(umlShape=umlClasses['DestClassA'])
        nodeB: RealSugiyamaNode = RealSugiyamaNode(umlShape=umlClasses['DestClassB'])
        linkA: SugiyamaLink     = SugiyamaLink(umlLink=umlLinks[0], umlFrame=self._diagramFrame)
        linkB: SugiyamaLink     = SugiyamaLink(umlLink=umlLinks[1], umlFrame=self._diagramFrame)

        edgeA: SugiyamaVertexEdge = SugiyamaVertexEdge((nodeA, linkA))
        edgeB: SugiyamaVertexEdge = SugiyamaVertexEdge((nodeB, linkB))
        vertexEdges: SugiyamaVertexEdges = SugiyamaVertexEdges([edgeA, edgeB])

        replacementNode: VirtualSugiyamaNode = VirtualSugiyamaNode()
        VirtualNodeInserter.updateLink(
            vertexEdges=vertexEdges,
            targetLink=linkA,
            replacementNode=replacementNode,
        )

        self.assertEqual(vertexEdges[0][0], replacementNode)
        self.assertEqual(vertexEdges[0][1], linkA)
        self.assertEqual(vertexEdges[1][0], nodeB)
        self.assertEqual(vertexEdges[1][1], linkB)

    def testUpdateLinkNoMatchLeavesEdgesUnchanged(self):
        """
        VirtualNodeInserter.updateLink should not modify any edges when the target link is not in the list.
        """
        umlShapes, umlClasses, umlLinks = self._buildGraph(
            nodeSpecs=[
                ('SourceClass', 100, 100),
                ('DestClass', 300, 100),
                ('UnrelatedClass', 500, 100),
            ],
            edgeSpecs=[
                ('SourceClass', 'DestClass', LinkType.INHERITANCE),
                ('SourceClass', 'UnrelatedClass', LinkType.ASSOCIATION),
            ],
        )
        node: RealSugiyamaNode = RealSugiyamaNode(umlShape=umlClasses['DestClass'])
        targetLink: SugiyamaLink = SugiyamaLink(umlLink=umlLinks[0], umlFrame=self._diagramFrame)
        unrelatedLink: SugiyamaLink = SugiyamaLink(umlLink=umlLinks[1], umlFrame=self._diagramFrame)

        edge: SugiyamaVertexEdge = SugiyamaVertexEdge((node, targetLink))
        vertexEdges: SugiyamaVertexEdges = SugiyamaVertexEdges([edge])

        replacementNode: VirtualSugiyamaNode = VirtualSugiyamaNode()
        VirtualNodeInserter.updateLink(
            vertexEdges=vertexEdges,
            targetLink=unrelatedLink,
            replacementNode=replacementNode,
        )

        self.assertEqual(vertexEdges[0][0], node)
        self.assertEqual(vertexEdges[0][1], targetLink)

    def testAddVirtualNodesOnHierarchicalLinkSingleSpanNoVirtualNodes(self):
        """
        VirtualNodeInserter.insert should not insert virtual nodes when span is <= 1 level.
        """
        umlShapes, umlClasses, umlLinks = self._buildGraph(
            nodeSpecs=[
                ('ParentClass', 100, 100),
                ('ChildClass', 100, 250),
            ],
            edgeSpecs=[
                ('ChildClass', 'ParentClass', LinkType.INHERITANCE),
            ],
        )
        parentNode: RealSugiyamaNode = RealSugiyamaNode(umlShape=umlClasses['ParentClass'])
        childNode: RealSugiyamaNode  = RealSugiyamaNode(umlShape=umlClasses['ChildClass'])
        parentNode.level = 0
        childNode.level  = 1

        hierarchicalLink: SugiyamaLink = SugiyamaLink(umlLink=umlLinks[0], umlFrame=self._diagramFrame)
        hierarchicalLink.source      = childNode
        hierarchicalLink.destination = parentNode
        parentNode.addChild(childNode, hierarchicalLink)
        childNode.addParent(parentNode, hierarchicalLink)

        levels: Levels = Levels([NodeList([parentNode]), NodeList([childNode])])
        virtualNodes: List[VirtualSugiyamaNode] = VirtualNodeInserter.insert(
            hierarchicalLink=hierarchicalLink,
            levels=levels,
        )

        self.assertEqual(len(virtualNodes), 0)
        self.assertEqual(len(levels[0]), 1)
        self.assertEqual(len(levels[1]), 1)
        self.assertEqual(self._countVirtualNodes(levels), 0)

    def testAddVirtualNodesOnHierarchicalLinkMultiLevelSpanInsertsVirtualNodes(self):
        """
        VirtualNodeInserter.insert should insert VirtualSugiyamaNodes across all intermediate levels
        and wire the child/parent chains to the endpoints.
        """
        umlShapes, umlClasses, umlLinks = self._buildGraph(
            nodeSpecs=[
                ('GrandParent', 100, 80),
                ('GrandChild', 100, 380),
            ],
            edgeSpecs=[
                ('GrandChild', 'GrandParent', LinkType.INHERITANCE),
            ],
        )
        grandParentNode: RealSugiyamaNode = RealSugiyamaNode(umlShape=umlClasses['GrandParent'])
        grandChildNode: RealSugiyamaNode  = RealSugiyamaNode(umlShape=umlClasses['GrandChild'])
        grandParentNode.level = 0
        grandChildNode.level  = 3

        hierarchicalLink: SugiyamaLink = SugiyamaLink(umlLink=umlLinks[0], umlFrame=self._diagramFrame)
        hierarchicalLink.source      = grandChildNode
        hierarchicalLink.destination = grandParentNode
        grandParentNode.addChild(grandChildNode, hierarchicalLink)
        grandChildNode.addParent(grandParentNode, hierarchicalLink)

        levels: Levels = Levels([
            NodeList([grandParentNode]),
            NodeList([]),
            NodeList([]),
            NodeList([grandChildNode]),
        ])

        virtualNodes: List[VirtualSugiyamaNode] = VirtualNodeInserter.insert(
            hierarchicalLink=hierarchicalLink,
            levels=levels,
        )

        self.assertEqual(len(virtualNodes), 2)

        # Levels 1 and 2 should each receive 1 virtual node
        self.assertEqual(len(levels[1]), 1)
        self.assertEqual(len(levels[2]), 1)

        node1: Nodes = levels[1][0]
        node2: Nodes = levels[2][0]
        self.assertIsInstance(node1, VirtualSugiyamaNode)
        self.assertIsInstance(node2, VirtualSugiyamaNode)
        assert isinstance(node1, VirtualSugiyamaNode)
        assert isinstance(node2, VirtualSugiyamaNode)

        virtualNode1: VirtualSugiyamaNode = node1
        virtualNode2: VirtualSugiyamaNode = node2

        # Verify level and index attributes
        self.assertEqual(virtualNode1.level, 1)
        self.assertEqual(virtualNode1.index, 0)
        self.assertEqual(virtualNode2.level, 2)
        self.assertEqual(virtualNode2.index, 0)

        # Verify parent / child relationships along the virtual chain
        # virtualNode1: parent is grandParentNode, child is virtualNode2
        self.assertEqual(len(virtualNode1.parents), 1)
        self.assertEqual(virtualNode1.parents[0][0], grandParentNode)
        self.assertEqual(len(virtualNode1.children), 1)
        self.assertEqual(virtualNode1.children[0][0], virtualNode2)

        # virtualNode2: parent is virtualNode1, child is grandChildNode
        self.assertEqual(len(virtualNode2.parents), 1)
        self.assertEqual(virtualNode2.parents[0][0], virtualNode1)
        self.assertEqual(len(virtualNode2.children), 1)
        self.assertEqual(virtualNode2.children[0][0], grandChildNode)

        # Real nodes endpoints updated via _updateLink
        self.assertEqual(grandParentNode.children[0][0], virtualNode1)
        self.assertEqual(grandChildNode.parents[0][0], virtualNode2)

        # Virtual nodes count
        self.assertEqual(self._countVirtualNodes(levels), 2)

    def testVirtualNodeInserterStepByStepLifecycle(self):
        """
        VirtualNodeInserter internal step methods should execute the lifecycle independently.
        """
        umlShapes, umlClasses, umlLinks = self._buildGraph(
            nodeSpecs=[
                ('RootNode', 100, 50),
                ('LeafNode', 100, 350),
            ],
            edgeSpecs=[
                ('LeafNode', 'RootNode', LinkType.INHERITANCE),
            ],
        )
        rootNode: RealSugiyamaNode = RealSugiyamaNode(umlShape=umlClasses['RootNode'])
        leafNode: RealSugiyamaNode = RealSugiyamaNode(umlShape=umlClasses['LeafNode'])
        rootNode.level = 0
        leafNode.level = 3

        hierarchicalLink: SugiyamaLink = SugiyamaLink(umlLink=umlLinks[0], umlFrame=self._diagramFrame)
        hierarchicalLink.source = leafNode
        hierarchicalLink.destination = rootNode
        rootNode.addChild(leafNode, hierarchicalLink)
        leafNode.addParent(rootNode, hierarchicalLink)

        levels: Levels = Levels([
            NodeList([rootNode]),
            NodeList([]),
            NodeList([]),
            NodeList([leafNode]),
        ])

        inserter: VirtualNodeInserter = VirtualNodeInserter(
            hierarchicalLink=hierarchicalLink,
            levels=levels,
        )
        self.assertEqual(len(inserter.virtualNodes), 0)

        hasCreated: bool = inserter._createVirtualNodes()
        self.assertTrue(hasCreated)
        self.assertEqual(len(inserter.virtualNodes), 2)
        self.assertEqual(inserter.virtualNodes[0].level, 1)
        self.assertEqual(inserter.virtualNodes[1].level, 2)

        inserter._connectVirtualChain()
        self.assertEqual(rootNode.children[0][0], inserter.virtualNodes[0])
        self.assertEqual(leafNode.parents[0][0], inserter.virtualNodes[1])

        inserter._registerInLevels()
        self.assertEqual(len(levels[1]), 1)
        self.assertEqual(len(levels[2]), 1)

        inserter._attachToLink()
        self.assertEqual(self._countVirtualNodes(levels), 2)


if __name__ == '__main__':
    main()
