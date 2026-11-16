"""
Generic reusable OGL shape event handler supporting real-time in-place dragging.
"""

from typing import Any
from typing import Callable
from typing import Generic
from typing import Optional
from typing import TypeVar

from wx import CallAfter

from wx.lib.ogl import LineShape
from wx.lib.ogl import Shape
from wx.lib.ogl import ShapeCanvas
from wx.lib.ogl import ShapeEvtHandler

ElementIdT = TypeVar('ElementIdT')


class ShapeDragEvtHandler(ShapeEvtHandler, Generic[ElementIdT]):
    """
    Reusable OGL event handler for live in-place shape dragging with connected-line updates.
    """

    def __init__(
        self,
        elementId:         ElementIdT,
        canvas:            ShapeCanvas,
        onPositionDragged: Optional[Callable[[ElementIdT, float, float], None]] = None,
        onPositionMoved:   Optional[Callable[[ElementIdT, float, float], None]] = None,
    ):
        """
        Initialize the shape drag event handler.

        Args:
            elementId: Identifier of the element represented by this shape.
            canvas: Hosting ShapeCanvas instance.
            onPositionDragged: Optional callback receiving (elementId, newX, newY) live during drag.
            onPositionMoved: Optional callback receiving (elementId, newX, newY) once drag ends.
        """
        super().__init__()
        self._elementId:         ElementIdT                                       = elementId
        self._canvas:            ShapeCanvas                                      = canvas
        self._onPositionDragged: Optional[Callable[[ElementIdT, float, float], None]] = onPositionDragged
        self._onPositionMoved:   Optional[Callable[[ElementIdT, float, float], None]] = onPositionMoved
        self._dragOffsetX:       float                                            = 0.0
        self._dragOffsetY:       float                                            = 0.0

    def OnBeginDragLeft(self, x: float, y: float, keys: int = 0, attachment: int = 0):
        """
        Begin dragging the shape and capture mouse input.

        Args:
            x: Initial X drag coordinate.
            y: Initial Y drag coordinate.
            keys: Modifier key bitmask.
            attachment: Attachment point index.
        """
        shape: Optional[Shape] = self.GetShape()
        if shape is not None:
            self._dragOffsetX = float(shape.GetX()) - float(x)
            self._dragOffsetY = float(shape.GetY()) - float(y)

        if not self._canvas.HasCapture():
            self._canvas.CaptureMouse()

    def OnDragLeft(self, draw: bool, x: float, y: float, keys: int = 0, attachment: int = 0):
        """
        Update the shape and its connected lines live while dragging.

        Args:
            draw: True on the draw pass of the drag step, False on the erase pass.
            x: Current X drag coordinate.
            y: Current Y drag coordinate.
            keys: Modifier key bitmask.
            attachment: Attachment point index.
        """
        if not draw:
            return

        newX: float = float(x) + self._dragOffsetX
        newY: float = float(y) + self._dragOffsetY

        self._updateShapeAndLines(newX, newY)

        if self._onPositionDragged is not None:
            self._onPositionDragged(self._elementId, newX, newY)

        self._canvas.Refresh()

    def OnEndDragLeft(self, x: float, y: float, keys: int = 0, attachment: int = 0):
        """
        Complete shape drag and notify the optional completion callback.

        Args:
            x: Final X drag coordinate.
            y: Final Y drag coordinate.
            keys: Modifier key bitmask.
            attachment: Attachment point index.
        """
        if self._canvas.HasCapture():
            self._canvas.ReleaseMouse()

        newX: float = float(x) + self._dragOffsetX
        newY: float = float(y) + self._dragOffsetY

        self._updateShapeAndLines(newX, newY)
        self._canvas.Refresh()

        if self._onPositionMoved is not None:
            callback: Callable[[ElementIdT, float, float], None] = self._onPositionMoved
            CallAfter(lambda: callback(self._elementId, newX, newY))

    def _updateShapeAndLines(self, newX: float, newY: float):
        """
        Move the attached shape and recompute endpoints for all connected lines.

        Args:
            newX: Updated X center coordinate.
            newY: Updated Y center coordinate.
        """
        shape: Optional[Shape] = self.GetShape()
        if shape is None:
            return

        shape.SetX(newX)
        shape.SetY(newY)

        line: LineShape
        for line in shape.GetLines():
            endPoints: Any = line.FindLineEndPoints()
            if endPoints is not None:
                line.SetEnds(endPoints[0], endPoints[1], endPoints[2], endPoints[3])
