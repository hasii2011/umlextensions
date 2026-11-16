"""
Main application window for the Sugiyama hierarchical layout visualizer.
"""

from typing import List

from wx import Button
from wx import Choice
from wx import CommandEvent
from wx import DEFAULT_FRAME_STYLE
from wx import EVT_BUTTON
from wx import EVT_CHOICE
from wx import FRAME_FLOAT_ON_PARENT
from wx import ID_ANY
from wx import Size
from wx import SplitterWindow
from wx import StaticText
from wx import StatusBar

from wx.lib.sized_controls import SizedFrame
from wx.lib.sized_controls import SizedPanel

from tests.sugiyamavisualizer.SugiyamaCanvasPanel import SugiyamaCanvasPanel
from tests.sugiyamavisualizer.SugiyamaDataSet import SugiyamaDataSet
from tests.sugiyamavisualizer.SugiyamaDataSet import createDefaultDataSets
from tests.sugiyamavisualizer.SugiyamaInspectorPanel import SugiyamaInspectorPanel

DEFAULT_FRAME_WIDTH:   int   = 1300
DEFAULT_FRAME_HEIGHT:  int   = 850
SPLITTER_SASH_RATIO:   float = 0.62
DEFAULT_SASH_POSITION: int   = int(DEFAULT_FRAME_WIDTH * SPLITTER_SASH_RATIO)
MINIMUM_PANE_SIZE:     int   = 250


class SugiyamaVisualizerFrame(SizedFrame):
    """
    Main application frame hosting toolbar controls, interactive canvas, and inspector notebook.
    """

    def __init__(self):
        """
        Construct the Sugiyama visualizer main frame.
        """
        super().__init__(
            None,
            ID_ANY,
            'Sugiyama Hierarchical Layout Visualizer',
            size=Size(DEFAULT_FRAME_WIDTH, DEFAULT_FRAME_HEIGHT),
            style=DEFAULT_FRAME_STYLE | FRAME_FLOAT_ON_PARENT
        )

        self._dataSets:            List[SugiyamaDataSet] = createDefaultDataSets()
        self._currentDataSetIndex: int                   = 0

        self._initUi()
        self._loadDataSet(0)

    def _initUi(self):
        """
        Construct the top-level toolbar, splitter, canvas, inspector, and status bar.
        """
        rootPanel: SizedPanel = self.GetContentsPane()
        rootPanel.SetSizerType('vertical')

        toolbarPanel: SizedPanel = SizedPanel(rootPanel, ID_ANY)
        toolbarPanel.SetSizerType('horizontal')
        toolbarPanel.SetSizerProps(expand=True)

        presetLabel: StaticText = StaticText(toolbarPanel, ID_ANY, 'Preset:')
        presetLabel.SetSizerProps(valign='center')

        presetNames: List[str] = [ds.name for ds in self._dataSets]
        self._presetChoice: Choice = Choice(toolbarPanel, ID_ANY, choices=presetNames)
        self._presetChoice.SetSelection(0)
        self._presetChoice.SetSizerProps(valign='center')
        self._presetChoice.Bind(EVT_CHOICE, self.onPresetChanged)

        self._resetButton: Button = Button(toolbarPanel, ID_ANY, 'Reset')
        self._resetButton.SetSizerProps(valign='center')
        self._resetButton.Bind(EVT_BUTTON, self.onReset)

        self._splitter: SplitterWindow = SplitterWindow(rootPanel, ID_ANY)
        self._splitter.SetSizerProps(expand=True, proportion=1)

        self._canvasPanel:    SugiyamaCanvasPanel    = SugiyamaCanvasPanel(self._splitter)
        self._inspectorPanel: SugiyamaInspectorPanel = SugiyamaInspectorPanel(self._splitter)

        self._splitter.SplitVertically(self._canvasPanel, self._inspectorPanel, DEFAULT_SASH_POSITION)
        self._splitter.SetMinimumPaneSize(MINIMUM_PANE_SIZE)

        self._statusBar: StatusBar = self.CreateStatusBar(2)
        self._statusBar.SetStatusWidths([-3, -2])
        self._statusBar.SetStatusText('Ready', 0)
        self._statusBar.SetStatusText('Phase: Initial', 1)

    def _loadDataSet(self, index: int):
        """
        Load and render the preset dataset at the given index.

        Args:
            index: Index into self._dataSets.
        """
        if index < 0 or index >= len(self._dataSets):
            return

        self._currentDataSetIndex = index
        dataSet: SugiyamaDataSet = self._dataSets[index]

        self._canvasPanel.renderDataSet(dataSet)
        self._inspectorPanel.showDataSet(dataSet)
        self._statusBar.SetStatusText(
            f'Loaded {dataSet.name}: {len(dataSet.nodes)} nodes, {len(dataSet.edges)} edges',
            0
        )
        self._statusBar.SetStatusText('Phase: Initial (unlaid)', 1)

    def onPresetChanged(self, _event: CommandEvent):
        """
        Handle preset selection changes.

        Args:
            _event: Choice selection event.
        """
        index: int = self._presetChoice.GetSelection()
        self._loadDataSet(index)

    def onReset(self, _event: CommandEvent):
        """
        Reset the active preset to its initial unlaid positions.

        Args:
            _event: Button click event.
        """
        self._loadDataSet(self._currentDataSetIndex)
