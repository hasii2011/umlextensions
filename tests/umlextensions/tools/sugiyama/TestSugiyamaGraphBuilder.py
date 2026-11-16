"""
Unit tests for SugiyamaGraphBuilder.
"""

from typing import Dict
from typing import List
from typing import Tuple

from unittest import main

from wx.lib.ogl import OGLInitialize

from codeallyadvanced.ui.UnitTestBaseW import UnitTestBaseW

from umlmodel.Class import Class
from umlmodel.Link import Link
from umlmodel.Note import Note
from umlmodel.enumerations.LinkType import LinkType

from umlshapes.ShapeTypes import UmlShapes
from umlshapes.ShapeTypes import umlShapesFactory
from umlshapes.frames.ClassDiagramFrame import ClassDiagramFrame
from umlshapes.links.UmlAssociation import UmlAssociation
from umlshapes.links.UmlInheritance import UmlInheritance
from umlshapes.links.UmlInterface import UmlInterface
from umlshapes.links.UmlLink import UmlLink
from umlshapes.pubsubengine.UmlPubSubEngine import UmlPubSubEngine
from umlshapes.shapes.UmlClass import UmlClass
from umlshapes.shapes.UmlNote import UmlNote
from umlshapes.types.UmlDimensions import UmlDimensions
from umlshapes.types.UmlPosition import UmlPosition

from umlextensions.tools.sugiyama.RealSugiyamaNode import RealSugiyamaNode
from umlextensions.tools.sugiyama.SugiyamaLink import SugiyamaLink
from umlextensions.tools.sugiyama.SugiyamaGraphBuilder import HierarchicalGraphNode
from umlextensions.tools.sugiyama.SugiyamaGraphBuilder import SugiyamaGraphBuilder

DEFAULT_NODE_WIDTH:  int = 120
DEFAULT_NODE_HEIGHT: int = 50


class TestSugiyamaGraphBuilder(UnitTestBaseW):
    """
    Unit tests covering canvas UML shape ingestion, node/link creation,
    hierarchical vs non-hierarchical classification, and node deduplication.
    """

    @classmethod
    def setUpClass(cls):
        """
        Initialize class-level test fixtures via UnitTestBaseW.
        """
        super().setUpClass()

    def setUp(self):
        """
        Create a fresh hidden ClassDiagramFrame for each test.
        """
        super().setUp()
        OGLInitialize()
        self._umlPubSubEngine: UmlPubSubEngine   = UmlPubSubEngine()
        self._diagramFrame:    ClassDiagramFrame = ClassDiagramFrame(
            parent=self._topLevelWindow,
            umlPubSubEngine=self._umlPubSubEngine,
        )
        self._diagramFrame.Hide()

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
                size=UmlDimensions(width=DEFAULT_NODE_WIDTH, height=DEFAULT_NODE_HEIGHT),
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
            elif linkType == LinkType.INTERFACE:
                ifaceLink: Link         = Link(linkType=LinkType.INTERFACE, source=srcClass.modelClass, destination=dstClass.modelClass)
                umlIface:  UmlInterface = UmlInterface(link=ifaceLink, interfaceClass=dstClass, implementingClass=srcClass)
                umlIface.SetCanvas(self._diagramFrame)
                umlIface.MakeLineControlPoints(2)
                srcClass.addLink(umlLink=umlIface, destinationClass=dstClass)
                self._diagramFrame.umlDiagram.AddShape(umlIface)
                umlShapes.append(umlIface)
                umlLinks.append(umlIface)
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

    def testEmptyDiagram(self):
        """
        An empty shape list should produce empty builder graph collections.
        """
        umlShapes: UmlShapes = umlShapesFactory()
        builder: SugiyamaGraphBuilder = SugiyamaGraphBuilder.build(
            umlShapes=umlShapes,
            umlFrame=self._diagramFrame,
        )

        self.assertEqual(len(builder.realNodes), 0)
        self.assertEqual(len(builder.links), 0)
        self.assertEqual(len(builder.hierarchicalNodes), 0)
        self.assertEqual(len(builder.nonHierarchicalNodes), 0)
        self.assertEqual(len(builder.nonHierarchicalLinks), 0)

    def testIsolatedClassesAndNotes(self):
        """
        Isolated classes and notes should be registered as real nodes and non-hierarchical nodes.
        """
        umlShapes: UmlShapes = umlShapesFactory()

        modelA: Class    = Class(name='ClassA')
        classA: UmlClass = UmlClass(modelClass=modelA, size=UmlDimensions(width=DEFAULT_NODE_WIDTH, height=DEFAULT_NODE_HEIGHT))
        classA.position = UmlPosition(x=100, y=100)
        classA.SetCanvas(self._diagramFrame)
        self._diagramFrame.umlDiagram.AddShape(classA)
        umlShapes.append(classA)

        modelB: Class    = Class(name='ClassB')
        classB: UmlClass = UmlClass(modelClass=modelB, size=UmlDimensions(width=DEFAULT_NODE_WIDTH, height=DEFAULT_NODE_HEIGHT))
        classB.position = UmlPosition(x=250, y=100)
        classB.SetCanvas(self._diagramFrame)
        self._diagramFrame.umlDiagram.AddShape(classB)
        umlShapes.append(classB)

        noteModel: Note    = Note()
        umlNote:   UmlNote = UmlNote(note=noteModel, size=UmlDimensions(width=DEFAULT_NODE_WIDTH, height=DEFAULT_NODE_HEIGHT))
        umlNote.position = UmlPosition(x=400, y=100)
        umlNote.SetCanvas(self._diagramFrame)
        self._diagramFrame.umlDiagram.AddShape(umlNote)
        umlShapes.append(umlNote)

        builder: SugiyamaGraphBuilder = SugiyamaGraphBuilder.build(
            umlShapes=umlShapes,
            umlFrame=self._diagramFrame,
        )

        self.assertEqual(len(builder.realNodes), 3)
        self.assertEqual(len(builder.links), 0)
        self.assertEqual(len(builder.hierarchicalNodes), 0)
        self.assertEqual(len(builder.nonHierarchicalNodes), 3)
        self.assertEqual(len(builder.nonHierarchicalLinks), 0)

    def testHierarchicalInheritanceLink(self):
        """
        Inheritance links should wire parent/child relations and register nodes in hierarchicalNodes.
        """
        umlShapes, umlClasses, umlLinks = self._buildGraph(
            nodeSpecs=[
                ('ParentClass', 100, 50),
                ('ChildClass', 100, 200),
            ],
            edgeSpecs=[
                ('ChildClass', 'ParentClass', LinkType.INHERITANCE),
            ],
        )

        builder: SugiyamaGraphBuilder = SugiyamaGraphBuilder.build(
            umlShapes=umlShapes,
            umlFrame=self._diagramFrame,
        )

        self.assertEqual(len(builder.realNodes), 2)
        self.assertEqual(len(builder.links), 1)
        self.assertEqual(len(builder.hierarchicalNodes), 2)
        self.assertEqual(len(builder.nonHierarchicalNodes), 0)
        self.assertEqual(len(builder.nonHierarchicalLinks), 0)

        childGraphNode:  HierarchicalGraphNode = builder.hierarchicalNodes[0]
        parentGraphNode: HierarchicalGraphNode = builder.hierarchicalNodes[1]
        assert isinstance(childGraphNode, RealSugiyamaNode)
        assert isinstance(parentGraphNode, RealSugiyamaNode)

        childNode:  RealSugiyamaNode = childGraphNode
        parentNode: RealSugiyamaNode = parentGraphNode
        link:       SugiyamaLink     = builder.links[0]

        # Verify parent and child relationships
        self.assertEqual(len(childNode.parents), 1)
        self.assertEqual(childNode.parents[0][0], parentNode)
        self.assertEqual(childNode.parents[0][1], link)

        self.assertEqual(len(parentNode.children), 1)
        self.assertEqual(parentNode.children[0][0], childNode)
        self.assertEqual(parentNode.children[0][1], link)

        # Verify link endpoints
        self.assertEqual(link.source, childNode)
        self.assertEqual(link.destination, parentNode)

    def testHierarchicalInterfaceLink(self):
        """
        Interface realization links should wire parent/child relations and register in hierarchicalNodes.
        """
        # noinspection SpellCheckingInspection
        umlShapes, umlClasses, umlLinks = self._buildGraph(
            nodeSpecs=[
                ('IService', 100, 50),
                ('ServiceImpl', 100, 200),
            ],
            edgeSpecs=[
                ('ServiceImpl', 'IService', LinkType.INTERFACE),
            ],
        )

        builder: SugiyamaGraphBuilder = SugiyamaGraphBuilder.build(
            umlShapes=umlShapes,
            umlFrame=self._diagramFrame,
        )

        self.assertEqual(len(builder.realNodes), 2)
        self.assertEqual(len(builder.links), 1)
        self.assertEqual(len(builder.hierarchicalNodes), 2)
        self.assertEqual(len(builder.nonHierarchicalNodes), 0)
        self.assertEqual(len(builder.nonHierarchicalLinks), 0)

        implGraphNode:  HierarchicalGraphNode = builder.hierarchicalNodes[0]
        ifaceGraphNode: HierarchicalGraphNode = builder.hierarchicalNodes[1]
        assert isinstance(implGraphNode, RealSugiyamaNode)
        assert isinstance(ifaceGraphNode, RealSugiyamaNode)

        implNode:  RealSugiyamaNode = implGraphNode
        ifaceNode: RealSugiyamaNode = ifaceGraphNode
        link:      SugiyamaLink     = builder.links[0]

        self.assertEqual(len(implNode.parents), 1)
        self.assertEqual(implNode.parents[0][0], ifaceNode)
        self.assertEqual(len(ifaceNode.children), 1)
        self.assertEqual(ifaceNode.children[0][0], implNode)
        self.assertEqual(link.source, implNode)
        self.assertEqual(link.destination, ifaceNode)

    def testNonHierarchicalAssociationLink(self):
        """
        Association links should wire non-hierarchical links and leave nodes in nonHierarchicalNodes.
        """
        umlShapes, umlClasses, umlLinks = self._buildGraph(
            nodeSpecs=[
                ('Customer', 100, 100),
                ('Order', 300, 100),
            ],
            edgeSpecs=[
                ('Customer', 'Order', LinkType.ASSOCIATION),
            ],
        )

        builder: SugiyamaGraphBuilder = SugiyamaGraphBuilder.build(
            umlShapes=umlShapes,
            umlFrame=self._diagramFrame,
        )

        self.assertEqual(len(builder.realNodes), 2)
        self.assertEqual(len(builder.links), 1)
        self.assertEqual(len(builder.hierarchicalNodes), 0)
        self.assertEqual(len(builder.nonHierarchicalNodes), 2)
        self.assertEqual(len(builder.nonHierarchicalLinks), 1)

        customerNode: RealSugiyamaNode = builder.realNodes[0]
        orderNode:    RealSugiyamaNode = builder.realNodes[1]
        link:         SugiyamaLink     = builder.links[0]

        # Verify non-hierarchical links wired in both directions
        self.assertEqual(len(customerNode.nonHierarchicalLinks), 1)
        self.assertEqual(customerNode.nonHierarchicalLinks[0][0], orderNode)
        self.assertEqual(customerNode.nonHierarchicalLinks[0][1], link)

        self.assertEqual(len(orderNode.nonHierarchicalLinks), 1)
        self.assertEqual(orderNode.nonHierarchicalLinks[0][0], customerNode)
        self.assertEqual(orderNode.nonHierarchicalLinks[0][1], link)

    def testNodeDeduplicationAcrossMultipleLinks(self):
        """
        Nodes connected by multiple links should be created only once and shared.
        """
        umlShapes, umlClasses, umlLinks = self._buildGraph(
            nodeSpecs=[
                ('Base', 200, 50),
                ('Child1', 100, 200),
                ('Child2', 300, 200),
                ('Helper', 400, 50),
            ],
            edgeSpecs=[
                ('Child1', 'Base', LinkType.INHERITANCE),
                ('Child2', 'Base', LinkType.INHERITANCE),
                ('Base', 'Helper', LinkType.ASSOCIATION),
            ],
        )

        builder: SugiyamaGraphBuilder = SugiyamaGraphBuilder.build(
            umlShapes=umlShapes,
            umlFrame=self._diagramFrame,
        )

        self.assertEqual(len(builder.realNodes), 4)
        self.assertEqual(len(builder.links), 3)
        self.assertEqual(len(builder.hierarchicalNodes), 3)
        self.assertEqual(len(builder.nonHierarchicalNodes), 1)
        self.assertEqual(len(builder.nonHierarchicalLinks), 1)

    def testMixedGraphPartitioning(self):
        """
        A diagram with inheritance, associations, and notes should partition cleanly.
        """
        umlShapes, umlClasses, umlLinks = self._buildGraph(
            nodeSpecs=[
                ('Base', 150, 50),
                ('Derived', 150, 200),
                ('Logger', 350, 200),
            ],
            edgeSpecs=[
                ('Derived', 'Base', LinkType.INHERITANCE),
                ('Derived', 'Logger', LinkType.ASSOCIATION),
            ],
        )

        noteModel: Note    = Note()
        umlNote:   UmlNote = UmlNote(note=noteModel, size=UmlDimensions(width=DEFAULT_NODE_WIDTH, height=DEFAULT_NODE_HEIGHT))
        umlNote.position = UmlPosition(x=350, y=50)
        umlNote.SetCanvas(self._diagramFrame)
        self._diagramFrame.umlDiagram.AddShape(umlNote)
        umlShapes.append(umlNote)

        builder: SugiyamaGraphBuilder = SugiyamaGraphBuilder.build(
            umlShapes=umlShapes,
            umlFrame=self._diagramFrame,
        )

        self.assertEqual(len(builder.realNodes), 4)
        self.assertEqual(len(builder.links), 2)
        self.assertEqual(len(builder.hierarchicalNodes), 2)
        self.assertEqual(len(builder.nonHierarchicalNodes), 2)
        self.assertEqual(len(builder.nonHierarchicalLinks), 1)


if __name__ == '__main__':
    main()
