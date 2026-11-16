"""
Preset graph datasets for the Sugiyama hierarchical layout visualizer.
"""

from dataclasses import dataclass
from typing import List

from umlmodel.enumerations.LinkType import LinkType

DEFAULT_NODE_WIDTH:  int = 120
DEFAULT_NODE_HEIGHT: int = 50


@dataclass(frozen=True)
class SugiyamaNodeSpec:
    """
    Specification for a single UML class node in a Sugiyama preset.
    """
    name:   str
    x:      int
    y:      int
    width:  int = DEFAULT_NODE_WIDTH
    height: int = DEFAULT_NODE_HEIGHT


@dataclass(frozen=True)
class SugiyamaEdgeSpec:
    """
    Specification for a directed edge between two nodes in a Sugiyama preset.
    """
    sourceName: str
    targetName: str
    linkType:   LinkType


@dataclass(frozen=True)
class SugiyamaDataSet:
    """
    Encapsulates a named UML graph preset for the Sugiyama visualizer.
    """
    name:        str
    description: str
    nodes:       List[SugiyamaNodeSpec]
    edges:       List[SugiyamaEdgeSpec]


def createDefaultDataSets() -> List[SugiyamaDataSet]:
    """
    Construct standard preset datasets covering trees, diamonds, multi-level spans, and mixed links.

    Returns:
        List of SugiyamaDataSet instances.
    """
    simpleTree: SugiyamaDataSet = SugiyamaDataSet(
        name='Simple Hierarchy (Tree)',
        description='Basic 3-level inheritance tree to show level assignment and balanced placement.',
        nodes=[
            SugiyamaNodeSpec(name='Animal', x=120, y=320),
            SugiyamaNodeSpec(name='Mammal', x=420, y=90),
            SugiyamaNodeSpec(name='Bird', x=60, y=90),
            SugiyamaNodeSpec(name='Dog', x=500, y=260),
            SugiyamaNodeSpec(name='Cat', x=260, y=180),
            SugiyamaNodeSpec(name='Eagle', x=260, y=380),
        ],
        edges=[
            SugiyamaEdgeSpec(sourceName='Mammal', targetName='Animal', linkType=LinkType.INHERITANCE),
            SugiyamaEdgeSpec(sourceName='Bird', targetName='Animal', linkType=LinkType.INHERITANCE),
            SugiyamaEdgeSpec(sourceName='Dog', targetName='Mammal', linkType=LinkType.INHERITANCE),
            SugiyamaEdgeSpec(sourceName='Cat', targetName='Mammal', linkType=LinkType.INHERITANCE),
            SugiyamaEdgeSpec(sourceName='Eagle', targetName='Bird', linkType=LinkType.INHERITANCE),
        ],
    )

    diamondPreset: SugiyamaDataSet = SugiyamaDataSet(
        name='Diamond / Multiple Inheritance',
        description='Diamond hierarchy with crossing edges to demonstrate barycenter crossing reduction.',
        nodes=[
            SugiyamaNodeSpec(name='Base', x=440, y=360),
            SugiyamaNodeSpec(name='LeftMixin', x=80, y=100),
            SugiyamaNodeSpec(name='RightMixin', x=480, y=100),
            SugiyamaNodeSpec(name='DiamondChild', x=280, y=220),
            SugiyamaNodeSpec(name='ExtraLeaf', x=100, y=340),
        ],
        edges=[
            SugiyamaEdgeSpec(sourceName='LeftMixin', targetName='Base', linkType=LinkType.INHERITANCE),
            SugiyamaEdgeSpec(sourceName='RightMixin', targetName='Base', linkType=LinkType.INHERITANCE),
            SugiyamaEdgeSpec(sourceName='DiamondChild', targetName='LeftMixin', linkType=LinkType.INHERITANCE),
            SugiyamaEdgeSpec(sourceName='DiamondChild', targetName='RightMixin', linkType=LinkType.INHERITANCE),
            SugiyamaEdgeSpec(sourceName='ExtraLeaf', targetName='LeftMixin', linkType=LinkType.INHERITANCE),
        ],
    )

    multiLevelSpan: SugiyamaDataSet = SugiyamaDataSet(
        name='Multi-Level Span (Virtual Nodes)',
        description='Long-span inheritance edges across 4 levels requiring VirtualSugiyamaNode insertion.',
        nodes=[
            SugiyamaNodeSpec(name='Root', x=80, y=80),
            SugiyamaNodeSpec(name='Layer1A', x=460, y=120),
            SugiyamaNodeSpec(name='Layer1B', x=260, y=240),
            SugiyamaNodeSpec(name='Layer2', x=100, y=340),
            SugiyamaNodeSpec(name='Leaf', x=480, y=340),
        ],
        edges=[
            SugiyamaEdgeSpec(sourceName='Layer1A', targetName='Root', linkType=LinkType.INHERITANCE),
            SugiyamaEdgeSpec(sourceName='Layer1B', targetName='Root', linkType=LinkType.INHERITANCE),
            SugiyamaEdgeSpec(sourceName='Layer2', targetName='Layer1A', linkType=LinkType.INHERITANCE),
            SugiyamaEdgeSpec(sourceName='Leaf', targetName='Layer2', linkType=LinkType.INHERITANCE),
            SugiyamaEdgeSpec(sourceName='Leaf', targetName='Root', linkType=LinkType.INHERITANCE),
            SugiyamaEdgeSpec(sourceName='Layer2', targetName='Root', linkType=LinkType.INHERITANCE),
        ],
    )

    mixedLinks: SugiyamaDataSet = SugiyamaDataSet(
        name='Mixed Hierarchy + Associations',
        description='Combines inheritance hierarchy with non-hierarchical association links.',
        nodes=[
            SugiyamaNodeSpec(name='AbstractHandler', x=100, y=300),
            SugiyamaNodeSpec(name='HttpHandler', x=440, y=100),
            SugiyamaNodeSpec(name='WsHandler', x=280, y=100),
            SugiyamaNodeSpec(name='Router', x=520, y=300),
            SugiyamaNodeSpec(name='Logger', x=100, y=100),
        ],
        edges=[
            SugiyamaEdgeSpec(sourceName='HttpHandler', targetName='AbstractHandler', linkType=LinkType.INHERITANCE),
            SugiyamaEdgeSpec(sourceName='WsHandler', targetName='AbstractHandler', linkType=LinkType.INHERITANCE),
            SugiyamaEdgeSpec(sourceName='Router', targetName='HttpHandler', linkType=LinkType.ASSOCIATION),
            SugiyamaEdgeSpec(sourceName='Router', targetName='WsHandler', linkType=LinkType.ASSOCIATION),
            SugiyamaEdgeSpec(sourceName='AbstractHandler', targetName='Logger', linkType=LinkType.ASSOCIATION),
        ],
    )

    return [simpleTree, diamondPreset, multiLevelSpan, mixedLinks]
