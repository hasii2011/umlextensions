"""
Interactive OGL canvas panel for the Sugiyama hierarchical layout visualizer.
"""

from typing import Dict
from typing import List
from typing import Tuple

from wx import Brush
from wx import Colour
from wx import FONTFAMILY_SWISS
from wx import FONTSTYLE_NORMAL
from wx import FONTWEIGHT_BOLD
from wx import FONTWEIGHT_NORMAL
from wx import Font
from wx import ID_ANY
from wx import Pen
from wx import PENSTYLE_DOT
from wx import PENSTYLE_SHORT_DASH
from wx import PENSTYLE_SOLID
from wx import RealPoint
from wx import WHITE
from wx import Window

from wx.lib.ogl import ARROW_ARROW
from wx.lib.ogl import ARROW_POSITION_END
from wx.lib.ogl import CircleShape
from wx.lib.ogl import Diagram
from wx.lib.ogl import LineShape
from wx.lib.ogl import RectangleShape
from wx.lib.ogl import Shape
from wx.lib.ogl import ShapeCanvas

from wx.lib.sized_controls import SizedPanel

from umlmodel.enumerations.LinkType import LinkType

from tests.sugiyamavisualizer.SugiyamaNodeEvtHandler import SugiyamaNodeEvtHandler
from tests.sugiyamavisualizer.SugiyamaStep import SugiyamaLinkSnapshot
from tests.sugiyamavisualizer.SugiyamaStep import SugiyamaNodeSnapshot
from tests.sugiyamavisualizer.SugiyamaStep import SugiyamaStepSnapshot

CANVAS_BACKGROUND_COLOUR: Colour = Colour(248, 250, 252)
LEVEL_BAND_EVEN_COLOUR:   Colour = Colour(241, 245, 249)
LEVEL_BAND_ODD_COLOUR:    Colour = Colour(226, 232, 240)
LEVEL_BAND_BORDER_COLOUR: Colour = Colour(203, 213, 225)
NODE_FILL_COLOUR:         Colour = Colour(219, 234, 254)
NODE_BORDER_COLOUR:       Colour = Colour(37, 99, 235)
VIRTUAL_NODE_FILL_COLOUR: Colour = Colour(254, 243, 199)
VIRTUAL_NODE_BORDER:      Colour = Colour(217, 119, 6)
CONTROL_POINT_COLOUR:     Colour = Colour(220, 38, 38)
INHERITANCE_EDGE_COLOUR:  Colour = Colour(30, 41, 59)
ASSOCIATION_EDGE_COLOUR:  Colour = Colour(100, 116, 139)

NODE_FONT_SIZE:         int   = 11
BADGE_FONT_SIZE:        int   = 9
NODE_BORDER_PX:         int   = 2
EDGE_PEN_WIDTH:         int   = 2
EDGE_ARROW_SIZE:        float = 10.0
CONTROL_POINT_DIAMETER: float = 8.0
LEVEL_BAND_X_PADDING:   float = 20.0
LEVEL_BAND_Y_PADDING:   float = 12.0
LEVEL_BAND_MIN_WIDTH:   float = 700.0


class SugiyamaCanvasPanel(SizedPanel):
    """
    Panel hosting the OGL ShapeCanvas and Diagram for rendering Sugiyama layouts.
    """

    def __init__(self, parent: Window):
        """
        Construct the Sugiyama canvas panel.

        Args:
            parent: Parent container widget.
        """
        super().__init__(parent, ID_ANY)
        self.SetSizerType('vertical')

        self._canvas: ShapeCanvas = ShapeCanvas(self, ID_ANY)
        self._canvas.SetSizerProps(expand=True, proportion=1)
        self._canvas.SetBackgroundColour(CANVAS_BACKGROUND_COLOUR)

        self._diagram: Diagram = Diagram()
        self._canvas.SetDiagram(self._diagram)
        self._diagram.SetCanvas(self._canvas)

        self._showLevelBands:       bool = True
        self._showVirtualNodes:     bool = True
        self._showBarycenterLabels: bool = True
        self._showControlPoints:    bool = True

    def setOverlayOptions(
        self,
        showLevelBands:       bool,
        showVirtualNodes:     bool,
        showBarycenterLabels: bool,
        showControlPoints:    bool,
    ):
        """
        Update overlay visibility flags.

        Args:
            showLevelBands: Whether to draw horizontal rank bands.
            showVirtualNodes: Whether to draw virtual node markers.
            showBarycenterLabels: Whether to append barycenter values to node labels.
            showControlPoints: Whether to draw intermediate link control points.
        """
        self._showLevelBands       = showLevelBands
        self._showVirtualNodes     = showVirtualNodes
        self._showBarycenterLabels = showBarycenterLabels
        self._showControlPoints    = showControlPoints

    def clearCanvas(self):
        """
        Remove all shapes from the diagram and refresh the canvas.
        """
        self._diagram.DeleteAllShapes()
        self._canvas.SetBackgroundColour(WHITE)
        self._canvas.SetBackgroundColour(CANVAS_BACKGROUND_COLOUR)
        self._canvas.Draw()
        self._canvas.Refresh()

    def renderStep(self, snapshot: SugiyamaStepSnapshot):
        """
        Render a SugiyamaStepSnapshot onto the OGL canvas with active overlays.

        Args:
            snapshot: The step snapshot to render.
        """
        self._diagram.DeleteAllShapes()

        if self._showLevelBands and len(snapshot.levels) > 0:
            self._renderLevelBands(snapshot.levels)

        nodeShapes: Dict[str, Shape] = {}

        levelRow: List[SugiyamaNodeSnapshot]
        for levelRow in snapshot.levels:
            nodeSnap: SugiyamaNodeSnapshot
            for nodeSnap in levelRow:
                if nodeSnap.isVirtual and not self._showVirtualNodes:
                    continue
                shape: Shape = self._createNodeShape(nodeSnap)
                nodeShapes[nodeSnap.name] = shape

        unleveledSnap: SugiyamaNodeSnapshot
        for unleveledSnap in snapshot.unleveledNodes:
            shape = self._createNodeShape(unleveledSnap)
            nodeShapes[unleveledSnap.name] = shape

        linkSnap: SugiyamaLinkSnapshot
        for linkSnap in snapshot.links:
            if linkSnap.sourceName not in nodeShapes or linkSnap.targetName not in nodeShapes:
                continue

            srcShape: Shape = nodeShapes[linkSnap.sourceName]
            dstShape: Shape = nodeShapes[linkSnap.targetName]

            line: LineShape = LineShape()
            if linkSnap.linkType == LinkType.INHERITANCE:
                line.SetPen(Pen(INHERITANCE_EDGE_COLOUR, EDGE_PEN_WIDTH, PENSTYLE_SOLID))
            else:
                line.SetPen(Pen(ASSOCIATION_EDGE_COLOUR, EDGE_PEN_WIDTH, PENSTYLE_SHORT_DASH))

            line.AddArrow(ARROW_ARROW, ARROW_POSITION_END, EDGE_ARROW_SIZE, 0.0, '')

            if self._showControlPoints and len(linkSnap.controlPoints) > 2:
                pts: List[Tuple[int, int]] = linkSnap.controlPoints
                line.MakeLineControlPoints(len(pts))
                linePts: List[RealPoint] = line.GetLineControlPoints()
                idx: int = 0
                for ptX, ptY in pts:
                    if idx < len(linePts):
                        linePts[idx] = RealPoint(float(ptX), float(ptY))
                    idx += 1
                self._renderControlPointMarkers(pts[1:-1])
            else:
                line.MakeLineControlPoints(2)

            srcShape.AddLine(line, dstShape)
            line.Show(True)
            self._diagram.AddShape(line)
            line.SetCanvas(self._canvas)

        self._diagram.ShowAll(True)
        self._canvas.SetBackgroundColour(WHITE)
        self._canvas.SetBackgroundColour(CANVAS_BACKGROUND_COLOUR)
        self._canvas.Draw()
        self._canvas.Refresh()

    def _renderLevelBands(self, levels: List[List[SugiyamaNodeSnapshot]]):
        """
        Draw horizontal shaded bands behind each Sugiyama level.

        Args:
            levels: Ordered list of node snapshots per level.
        """
        bandFont: Font = Font(BADGE_FONT_SIZE, FONTFAMILY_SWISS, FONTSTYLE_NORMAL, FONTWEIGHT_NORMAL)
        levelIdx: int  = 0
        levelRow: List[SugiyamaNodeSnapshot]
        for levelRow in levels:
            if len(levelRow) == 0:
                levelIdx += 1
                continue

            minY: int = min(n.y for n in levelRow)
            maxY: int = max(n.y + n.height for n in levelRow)
            maxX: int = max(n.x + n.width for n in levelRow)

            bandWidth:  float = max(LEVEL_BAND_MIN_WIDTH, float(maxX) + LEVEL_BAND_X_PADDING)
            bandHeight: float = float(maxY - minY) + 2.0 * LEVEL_BAND_Y_PADDING
            bandCenterY: float = float(minY) + float(maxY - minY) / 2.0

            bandShape: RectangleShape = RectangleShape(bandWidth, bandHeight)
            bandShape.SetX(bandWidth / 2.0)
            bandShape.SetY(bandCenterY)
            if levelIdx % 2 == 0:
                bandShape.SetBrush(Brush(LEVEL_BAND_EVEN_COLOUR))
            else:
                bandShape.SetBrush(Brush(LEVEL_BAND_ODD_COLOUR))
            bandShape.SetPen(Pen(LEVEL_BAND_BORDER_COLOUR, 1, PENSTYLE_DOT))
            bandShape.SetFont(bandFont)
            bandShape.AddText(f'L{levelIdx}')
            bandShape.SetDraggable(False)
            bandShape.Show(True)
            self._diagram.AddShape(bandShape)
            bandShape.SetCanvas(self._canvas)
            levelIdx += 1

    def _createNodeShape(self, nodeSnap: SugiyamaNodeSnapshot) -> Shape:
        """
        Create and add an OGL shape for a real or virtual Sugiyama node.

        Args:
            nodeSnap: Node snapshot to render.

        Returns:
            The created OGL Shape.
        """
        shape: Shape
        if nodeSnap.isVirtual:
            circle: CircleShape = CircleShape(float(nodeSnap.width))
            circle.SetX(float(nodeSnap.x) + float(nodeSnap.width) / 2.0)
            circle.SetY(float(nodeSnap.y) + float(nodeSnap.height) / 2.0)
            circle.SetBrush(Brush(VIRTUAL_NODE_FILL_COLOUR))
            circle.SetPen(Pen(VIRTUAL_NODE_BORDER, NODE_BORDER_PX))
            circle.SetFont(Font(BADGE_FONT_SIZE, FONTFAMILY_SWISS, FONTSTYLE_NORMAL, FONTWEIGHT_BOLD))
            circle.AddText(nodeSnap.name)
            shape = circle
        else:
            rect: RectangleShape = RectangleShape(float(nodeSnap.width), float(nodeSnap.height))
            rect.SetX(float(nodeSnap.x) + float(nodeSnap.width) / 2.0)
            rect.SetY(float(nodeSnap.y) + float(nodeSnap.height) / 2.0)
            rect.SetBrush(Brush(NODE_FILL_COLOUR))
            rect.SetPen(Pen(NODE_BORDER_COLOUR, NODE_BORDER_PX))
            rect.SetFont(Font(NODE_FONT_SIZE, FONTFAMILY_SWISS, FONTSTYLE_NORMAL, FONTWEIGHT_BOLD))
            label: str = nodeSnap.name
            if self._showBarycenterLabels and nodeSnap.level >= 0:
                label = f'{nodeSnap.name}\n[bc={nodeSnap.barycenter:.1f}]'
            rect.AddText(label)
            shape = rect

        shape.SetDraggable(True, True)
        evtHandler: SugiyamaNodeEvtHandler = SugiyamaNodeEvtHandler(
            elementId=nodeSnap.name,
            canvas=self._canvas,
        )
        evtHandler.SetShape(shape)
        evtHandler.SetPreviousHandler(shape.GetEventHandler())
        shape.SetEventHandler(evtHandler)
        shape.Show(True)
        self._diagram.AddShape(shape)
        shape.SetCanvas(self._canvas)
        return shape

    def _renderControlPointMarkers(self, intermediatePoints: List[Tuple[int, int]]):
        """
        Draw small circular markers at intermediate link control points.

        Args:
            intermediatePoints: List of (x, y) coordinates.
        """
        ptX: int
        ptY: int
        for ptX, ptY in intermediatePoints:
            marker: CircleShape = CircleShape(CONTROL_POINT_DIAMETER)
            marker.SetX(float(ptX))
            marker.SetY(float(ptY))
            marker.SetBrush(Brush(CONTROL_POINT_COLOUR))
            marker.SetPen(Pen(CONTROL_POINT_COLOUR, 1))
            marker.SetDraggable(False)
            marker.Show(True)
            self._diagram.AddShape(marker)
            marker.SetCanvas(self._canvas)
