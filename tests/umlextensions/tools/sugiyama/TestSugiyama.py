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
from umlextensions.tools.sugiyama.VirtualSugiyamaNode import VirtualSugiyamaNode

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
        sugiyama.createInterfaceUmlShapeLayout(umlShapes=umlShapes)
        ok: bool = sugiyama.levelFind()
        if not ok:
            return sugiyama, False
        sugiyama.addVirtualNodes()
        sugiyama.barycenter()
        sugiyama.addNonHierarchicalNodes()
        sugiyama.fixPositions()
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
                posX, posY = node.getPosition()
                width, height = node.getSize()
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
        sugiyama.createInterfaceUmlShapeLayout(umlShapes=umlShapes)
        self.assertTrue(sugiyama.levelFind())
        sugiyama.addVirtualNodes()

        initialCrossings: int = sugiyama._getNbIntersectAll()
        sugiyama.barycenter()

        finalCrossings: int = sugiyama._getNbIntersectAll()
        self.assertGreaterEqual(initialCrossings, 1)
        self.assertEqual(finalCrossings, 0)
        sugiyama.addNonHierarchicalNodes()
        sugiyama.fixPositions()
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
        sugiyama.createInterfaceUmlShapeLayout(umlShapes=umlShapes)
        self.assertTrue(sugiyama.levelFind())
        sugiyama.addVirtualNodes()
        sugiyama.barycenter()
        totalBefore: int = sum(len(row) for row in sugiyama.levels)
        self.assertEqual(totalBefore, 3)

        sugiyama.addNonHierarchicalNodes()
        totalAfter: int = sum(len(row) for row in sugiyama.levels)
        self.assertEqual(totalAfter, 5)

        sugiyama.fixPositions()
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
        sugiyama.createInterfaceUmlShapeLayout(umlShapes=umlShapes)
        self.assertFalse(sugiyama.levelFind())


if __name__ == '__main__':
    main()
