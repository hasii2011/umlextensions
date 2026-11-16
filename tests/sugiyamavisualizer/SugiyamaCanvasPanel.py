"""
Interactive OGL canvas panel for the Sugiyama hierarchical layout visualizer.
"""

from typing import Dict

from wx import Brush
from wx import Colour
from wx import FONTFAMILY_SWISS
from wx import FONTSTYLE_NORMAL
from wx import FONTWEIGHT_BOLD
from wx import Font
from wx import ID_ANY
from wx import Pen
from wx import PENSTYLE_SHORT_DASH
from wx import PENSTYLE_SOLID
from wx import WHITE
from wx import Window

from wx.lib.ogl import ARROW_ARROW
from wx.lib.ogl import ARROW_POSITION_END
from wx.lib.ogl import Diagram
from wx.lib.ogl import LineShape
from wx.lib.ogl import RectangleShape
from wx.lib.ogl import ShapeCanvas

from wx.lib.sized_controls import SizedPanel

from umlmodel.enumerations.LinkType import LinkType

from tests.sugiyamavisualizer.SugiyamaDataSet import SugiyamaDataSet
from tests.sugiyamavisualizer.SugiyamaDataSet import SugiyamaEdgeSpec
from tests.sugiyamavisualizer.SugiyamaDataSet import SugiyamaNodeSpec
from tests.sugiyamavisualizer.SugiyamaNodeEvtHandler import SugiyamaNodeEvtHandler

CANVAS_BACKGROUND_COLOUR: Colour = Colour(248, 250, 252)
NODE_FILL_COLOUR:         Colour = Colour(219, 234, 254)
NODE_BORDER_COLOUR:       Colour = Colour(37, 99, 235)
INHERITANCE_EDGE_COLOUR:  Colour = Colour(30, 41, 59)
ASSOCIATION_EDGE_COLOUR:  Colour = Colour(100, 116, 139)

NODE_FONT_SIZE:  int   = 11
NODE_BORDER_PX:  int   = 2
EDGE_PEN_WIDTH:  int   = 2
EDGE_ARROW_SIZE: float = 10.0


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

    def clearCanvas(self):
        """
        Remove all shapes from the diagram and refresh the canvas.
        """
        self._diagram.DeleteAllShapes()
        self._canvas.SetBackgroundColour(WHITE)
        self._canvas.SetBackgroundColour(CANVAS_BACKGROUND_COLOUR)
        self._canvas.Draw()
        self._canvas.Refresh()

    def renderDataSet(self, dataSet: SugiyamaDataSet):
        """
        Render the initial unlaid nodes and edges of a preset dataset onto the OGL canvas.

        Args:
            dataSet: The preset graph dataset to render.
        """
        self._diagram.DeleteAllShapes()

        nodeShapes: Dict[str, RectangleShape] = {}
        nodeFont:   Font = Font(NODE_FONT_SIZE, FONTFAMILY_SWISS, FONTSTYLE_NORMAL, FONTWEIGHT_BOLD)
        nodeBrush:  Brush = Brush(NODE_FILL_COLOUR)
        nodePen:    Pen   = Pen(NODE_BORDER_COLOUR, NODE_BORDER_PX)

        nodeSpec: SugiyamaNodeSpec
        for nodeSpec in dataSet.nodes:
            shape: RectangleShape = RectangleShape(float(nodeSpec.width), float(nodeSpec.height))
            shape.SetX(float(nodeSpec.x) + float(nodeSpec.width) / 2.0)
            shape.SetY(float(nodeSpec.y) + float(nodeSpec.height) / 2.0)
            shape.SetBrush(nodeBrush)
            shape.SetPen(nodePen)
            shape.SetFont(nodeFont)
            shape.AddText(nodeSpec.name)
            shape.SetDraggable(True, True)
            evtHandler: SugiyamaNodeEvtHandler = SugiyamaNodeEvtHandler(
                elementId=nodeSpec.name,
                canvas=self._canvas,
            )
            evtHandler.SetShape(shape)
            evtHandler.SetPreviousHandler(shape.GetEventHandler())
            shape.SetEventHandler(evtHandler)
            shape.Show(True)
            self._diagram.AddShape(shape)
            shape.SetCanvas(self._canvas)
            nodeShapes[nodeSpec.name] = shape

        edgeSpec: SugiyamaEdgeSpec
        for edgeSpec in dataSet.edges:
            if edgeSpec.sourceName not in nodeShapes or edgeSpec.targetName not in nodeShapes:
                continue

            srcShape: RectangleShape = nodeShapes[edgeSpec.sourceName]
            dstShape: RectangleShape = nodeShapes[edgeSpec.targetName]

            line: LineShape = LineShape()
            if edgeSpec.linkType == LinkType.INHERITANCE:
                line.SetPen(Pen(INHERITANCE_EDGE_COLOUR, EDGE_PEN_WIDTH, PENSTYLE_SOLID))
                line.AddArrow(ARROW_ARROW, ARROW_POSITION_END, EDGE_ARROW_SIZE, 0.0, '')
            else:
                line.SetPen(Pen(ASSOCIATION_EDGE_COLOUR, EDGE_PEN_WIDTH, PENSTYLE_SHORT_DASH))
                line.AddArrow(ARROW_ARROW, ARROW_POSITION_END, EDGE_ARROW_SIZE, 0.0, '')

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
