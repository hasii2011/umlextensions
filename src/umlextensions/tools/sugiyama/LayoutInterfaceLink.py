
from typing import List

from typing import cast

from umlmodel.enumerations.LinkType import LinkType

from umlshapes.links.UmlAssociation import UmlAssociation
from umlshapes.links.UmlLink import UmlLink

from umlshapes.shapes.UmlLineControlPoint import UmlLineControlPoint
from wx import Point

from umlextensions.tools.sugiyama.LayoutGeometry import LayoutPosition
from umlextensions.tools.sugiyama.RealSugiyamaNode import RealSugiyamaNode
from umlextensions.tools.sugiyama.VirtualSugiyamaNode import VirtualSugiyamaNode

SyntheticNode = RealSugiyamaNode | VirtualSugiyamaNode


class LayoutInterfaceLink:
    """
    Interface between Uml Links and Layout algorithms.

    Layout algorithms use this interface to access the links on the
    diagram.

    * The interface protects the structure of the diagram.
    * The diagram structure and diagram m methods can be changed.

    Thus, we only need to update is this interface, not the automatic layout algorithm.

    Note:
        This happened in 2025, when Humberto did away with the miniogl home-grown code and
        instead used wxPython's wx.lib.ogl code
    """
    def __init__(self, umlLink: UmlLink):
        """

        Args:
            umlLink:
        """
        self._umlLink: UmlLink = umlLink
        self._srcNode: SyntheticNode = cast(SyntheticNode, cast(object, None))
        self._dstNode: SyntheticNode = cast(SyntheticNode, cast(object, None))

    @property
    def umlLink(self) -> UmlLink:
        """
        Return the underlying UML link.

        Returns:
            The wrapped UmlLink instance.
        """
        return self._umlLink

    @property
    def linkType(self) -> LinkType:
        """
        Return the link type

        Returns: Link type
        """
        return self._umlLink.modelLink.linkType

    @property
    def source(self) -> SyntheticNode:
        """

        Returns:  the source node.
        """
        return self._srcNode

    @source.setter
    def source(self, node: SyntheticNode):
        """
        Set the source node.

        Args:
            node:  The link source node
        """
        self._srcNode = node

    @property
    def destination(self) -> SyntheticNode:
        """

        Returns: The destination node
        """
        return self._dstNode

    @destination.setter
    def destination(self, node: SyntheticNode):
        """
        Set the destination node.

        Args:
            node: The new link destination
        """
        self._dstNode = node

    @property
    def sourcePosition(self) -> LayoutPosition:
        """
        Get the source endpoint position in absolute coordinates.

        Returns: LayoutPosition of the source end
        """
        umLink: UmlLink = self._umlLink
        x1: int
        y1: int
        x1, y1, _, _ = umLink.GetEnds()
        return LayoutPosition(x=x1, y=y1)

    @sourcePosition.setter
    def sourcePosition(self, pos: LayoutPosition):
        """
        Set the source endpoint position in absolute coordinates.

        Args:
            pos: New source LayoutPosition
        """
        umLink: UmlLink = self._umlLink
        x2: int
        y2: int
        _, _, x2, y2 = umLink.GetEnds()
        umLink.SetEnds(x1=pos.x, y1=pos.y, x2=x2, y2=y2)

    @property
    def destinationPosition(self) -> LayoutPosition:
        """
        Get the destination endpoint position in absolute coordinates.

        Returns: LayoutPosition of the destination end
        """
        umLink: UmlLink = self._umlLink
        x2: int
        y2: int
        _, _, x2, y2 = umLink.GetEnds()
        return LayoutPosition(x=x2, y=y2)

    @destinationPosition.setter
    def destinationPosition(self, pos: LayoutPosition):
        """
        Set the destination endpoint position in absolute coordinates.

        Args:
            pos: New destination LayoutPosition
        """
        umLink: UmlLink = self._umlLink
        x1: int
        y1: int
        x1, y1, _, _ = umLink.GetEnds()
        umLink.SetEnds(x1=x1, y1=y1, x2=pos.x, y2=pos.y)

    def addControlPoint(self, control: UmlLineControlPoint):
        """
        Add a control point. If the parameter last present, add a point right after last.

        Args:
            control:  control point to add
        """
        self._umlLink.addLineControlPoint(umlPosition=control.position)

    def removeAllControlPoints(self):
        """
        Remove all intermediate control points and their handles, preserving the two endpoints.
        """
        self._umlLink.DeleteControlPoints()
        lineControlPoints: List[Point] = self._umlLink.GetLineControlPoints()
        if len(lineControlPoints) > 2:
            firstPoint: Point = lineControlPoints[0]
            lastPoint:  Point = lineControlPoints[-1]
            lineControlPoints.clear()
            lineControlPoints.extend([firstPoint, lastPoint])

    def finalizeControlPoints(self):
        """
        Recreate draggable control point handles and reposition association labels
        after control points have been updated.
        """
        self._umlLink.MakeControlPoints()
        if isinstance(self._umlLink, UmlAssociation):
            self._umlLink.smartPlaceLabels()
