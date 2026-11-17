
from typing import Tuple

from umlextensions.tools.sugiyama.LayoutInterfaceNode import LayoutPosition
from umlextensions.tools.sugiyama.LayoutInterfaceNode import LayoutInterfaceNode

from umlextensions.tools.sugiyama.SugiyamaGlobals import SugiyamaGlobals
from umlextensions.tools.sugiyama.SugiyamaNode import SugiyamaNode
from umlextensions.tools.sugiyama.SugiyamaNode import SugiyamaVertexEdges


class RealSugiyamaNode(SugiyamaNode):
    """
    RealSugiyamaNode: A RealSugiyamaNode object is a node of the Sugiyama
    graph associated to an OglObject of the UML diagram, which can be a
    class or a note.

    For more information, see ../ToSugiyama.py

    Instantiated by: ../ToSugiyama.py

    :author: Nicolas Dubois
    :contact: nicdub@gmx.ch
    :version: $Revision: 1.4 $
    """
    def __init__(self, oglObject):
        """

        Args:
            oglObject: oglObject: diagram class or note
        """
        super().__init__()

        self.__aLayoutNode = LayoutInterfaceNode(oglObject)

    @property
    def size(self) -> Tuple[int, int]:
        """
        Get the size of the node.

        Returns: (int, int) : tuple (width, height)
        """
        return self.__aLayoutNode.size

    @property
    def position(self) -> Tuple[int, int]:
        """
        Get node position.

        Returns: (int, int) : tuple (x, y) in absolute coordinates
        """
        return self.__aLayoutNode.position.x, self.__aLayoutNode.position.y

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
        self.__aLayoutNode.position = LayoutPosition(x=xCoord, y=yCoord)

    @property
    def name(self) -> str:
        """
        The name of the OglObject.

        Returns:  Name of the UML Shape
        """
        return self.__aLayoutNode.name

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
