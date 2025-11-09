
from typing import List
from typing import Tuple

from pyutmodelv2.enumerations.PyutLinkType import PyutLinkType

from umlshapes.links.UmlLink import UmlLink

from umlshapes.shapes.UmlLineControlPoint import UmlLineControlPoint


class ALayoutLink:
    """
    ALayoutLink : Interface between Uml Links and Layout algorithms.

    Layout algorithms can use this interface to access the links on the
    diagram. The first reason is that the interface protects the structure
    of the diagram. The second is that pyut structure and methods could
    be changed. In a such case, the only files to update is the interface, not
    your automatic layout algorithm.

    """
    def __init__(self, umlLink: UmlLink):
        """

        Args:
            umlLink:
        """
        self._umlLink: UmlLink = umlLink
        self.__srcNode = None
        self.__dstNode = None

    def setSource(self, node):
        """
        Set the source node.

        @param InterfaceSugiyamaNode node: source node of the link
        @author Nicolas Dubois
        """
        self.__srcNode = node

    def getSource(self):
        """
        Return the source node.

        @return InterfaceSugiyamaNode: source node of the link
        @author Nicolas Dubois
        """
        return self.__srcNode

    def setDestination(self, node):
        """
        Set the destination node.

        @param InterfaceSugiyamaNode node: destination node of the link
        @author Nicolas Dubois
        """
        self.__dstNode = node

    def getDestination(self):
        """
        Return the destination node.

        @return InterfaceSugiyamaNode: destination node of the link
        @author Nicolas Dubois
        """
        return self.__dstNode

    def setSrcAnchorPos(self, x: int, y: int):
        """
        Set anchor position (absolute coordinates) on source class.

        Args:
            x:
            y:
        """
        umLink: UmlLink = self._umlLink
        x1, y1, x2, y2 = umLink.GetEnds()

        umLink.SetEnds(x1=x, y1=y, x2=x2, y2=y2)
        # self._umlLink.sourceAnchor.SetPosition(x, y)

    def setDestAnchorPos(self, x: int, y: int):
        """
        Set anchor position (absolute coordinates) on destination class.

        Args:
            x:
            y:
        """
        umLink: UmlLink = self._umlLink
        x1, y1, x2, y2 = umLink.GetEnds()

        umLink.SetEnds(x1=x1, y1=y1, x2=x, y2=y)

        # self._umlLink.destinationAnchor.SetPosition(x, y)

    def getSrcAnchorPos(self):
        """
        Get anchor position (absolute coordinates) on source class.

        Returns:    (int, int) : tuple with (x, y) coordinates
        """
        umLink: UmlLink = self._umlLink
        x1, y1, x2, y2 = umLink.GetEnds()

        return x1, y1
        # return self._umlLink.sourceAnchor.GetPosition()

    def getDestAnchorPos(self):
        """
        Return anchor position (absolute coordinates) on destination class.

        Returns:  (int, int) : tuple with (x, y) coordinates
        """
        umLink: UmlLink = self._umlLink
        x1, y1, x2, y2 = umLink.GetEnds()

        return x2, y2

    # noinspection PyUnusedLocal
    def addControlPoint(self, control: UmlLineControlPoint, last=None):
        """
        Add a control point. If the parameter last present, add a point right after last.
        TODO: the 'last' parameter is used by no one

        Args:
            control:  control point to add
            last:     add control right after last
        """
        # self._oglLink.AddControl(control, last)
        pt: Tuple[int, int] = control.position.x, control.position.y
        self._umlLink.InsertLineControlPoint(point=pt)

    def removeControlPoint(self, controlPoint):
        """
        Remove a control point.

        TODO:  This is not used by the Sugiyama algorithm

        Args:
            controlPoint: control point to remove
        """
        umlLink: UmlLink = self._umlLink

        controlPoints: List[UmlLineControlPoint] = umlLink.GetLineControlPoints()
        controlPoints.remove(controlPoint)

        # self._umlLink.Remove(controlPoint)

    def removeAllControlPoints(self):
        """
        Remove all control points.
        """
        # self._umlLink.ResetControlPoints()
        self._umlLink.DeleteControlPoints()
        # self._umlLink.RemoveAllControlPoints()

    @property
    def linkType(self) -> PyutLinkType:
        """
        Return the link type

        Returns: Link type
        """
        return self._umlLink.pyutLink.linkType
