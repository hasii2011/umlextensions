
from typing import Tuple

from umlshapes.ShapeTypes import UmlShape

from umlextensions.tools.sugiyama.LayoutInterfaceNode import LayoutPosition
from umlextensions.tools.sugiyama.LayoutInterfaceNode import LayoutSize
from umlextensions.tools.sugiyama.LayoutInterfaceNode import LayoutInterfaceNode

from umlextensions.tools.sugiyama.SugiyamaGlobals import SugiyamaGlobals
from umlextensions.tools.sugiyama.SugiyamaNode import SugiyamaNode
from umlextensions.tools.sugiyama.SugiyamaNode import SugiyamaVertexEdges


class RealSugiyamaNode(SugiyamaNode):
    """
    A real node in the Sugiyama layout graph associated with an actual UML
    shape (such as a class or note) in the diagram.
    """
    def __init__(self, umlShape: UmlShape):
        """
        Initialize a real Sugiyama node wrapping the given UML shape.

        Args:
            umlShape: The UML shape (such as a class or note) to wrap for layout.
        """
        super().__init__()

        self._layoutInterfaceNode: LayoutInterfaceNode = LayoutInterfaceNode(umlShape)

    @property
    def size(self) -> Tuple[int, int]:
        """
        Get the size of the node.

        Returns: (int, int) : tuple (width, height)
        """
        layoutSize: LayoutSize = self._layoutInterfaceNode.size
        return layoutSize.width, layoutSize.height

    @property
    def position(self) -> Tuple[int, int]:
        """
        Get node position.

        Returns: (int, int) : tuple (x, y) in absolute coordinates
        """
        return self._layoutInterfaceNode.position.x, self._layoutInterfaceNode.position.y

    @position.setter
    def position(self, pos: Tuple[int, int]):
        """
        Set node position.

        Args:
            pos: (x, y) position in absolute coordinates
        """
        xCoord: int
        yCoord: int
        xCoord, yCoord = pos
        self._layoutInterfaceNode.position = LayoutPosition(x=xCoord, y=yCoord)

    @property
    def name(self) -> str:
        """
        The name of the underlying UML shape.

        Returns: Name of the UML shape.
        """
        return self._layoutInterfaceNode.name

    def fixAnchorPos(self):
        """
        Fix the positions of the anchor points.

        The anchor points are placed according to parent and child positions.
        Before calling this method, be sure you have set the indices of all
        parent and children (see index property).

        """
        # Get position and size of node
        (width, height) = self.size
        (x, y) = self.position

        # Fix all children anchors position
        # Sort child list to eliminate crossing
        children: SugiyamaVertexEdges = self.children
        children.sort(key=SugiyamaGlobals.cmpIndex)

        nChildren: int = len(children)
        # For all children
        for i in range(nChildren):
            (child, link) = children[i]
            # Fix anchors coordinates
            link.setDestAnchorPos(x + width * (i + 1) // (nChildren + 1), y + height)

        # Parent anchors position
        # Sort parents list to eliminate crossing
        parents: SugiyamaVertexEdges = self.parents
        parents.sort(key=SugiyamaGlobals.cmpIndex)
        nParents: int = len(parents)
        # For all parents
        for i in range(nParents):
            (parent, link) = parents[i]
            # Fix anchors coordinates
            link.setSrcAnchorPos(x + width * (i + 1) // (nParents + 1), y)

    def __repr__(self) -> str:
        return f'RealSugiyamaNode name: {self.name} level: {self.level}'
