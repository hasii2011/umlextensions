"""
Main application window for the Sugiyama hierarchical layout visualizer.
"""

from typing import List

from wx import Button
from wx import CheckBox
from wx import Choice
from wx import CommandEvent
from wx import DEFAULT_FRAME_STYLE
from wx import EVT_BUTTON
from wx import EVT_CHECKBOX
from wx import EVT_CHOICE
from wx import FRAME_FLOAT_ON_PARENT
from wx import ID_ANY
from wx import Size
from wx import SplitterWindow
from wx import StaticText
from wx import StatusBar

from wx.lib.sized_controls import SizedFrame
from wx.lib.sized_controls import SizedPanel

from umlshapes.frames.ClassDiagramFrame import ClassDiagramFrame
from umlshapes.pubsubengine.UmlPubSubEngine import UmlPubSubEngine

from tests.extensiondemo.ExtensionsFacade import ExtensionsFacade
from tests.sugiyamavisualizer.SugiyamaCanvasPanel import SugiyamaCanvasPanel
from tests.sugiyamavisualizer.SugiyamaDataSet import SugiyamaDataSet
from tests.sugiyamavisualizer.SugiyamaDataSet import createDefaultDataSets
from tests.sugiyamavisualizer.SugiyamaInspectorPanel import SugiyamaInspectorPanel
from tests.sugiyamavisualizer.SugiyamaStep import SugiyamaStepSnapshot
from tests.sugiyamavisualizer.SugiyamaStep import SugiyamaStepper

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

        self._dataSets:            List[SugiyamaDataSet]      = createDefaultDataSets()
        self._currentDataSetIndex: int                        = 0
        self._steps:               List[SugiyamaStepSnapshot] = []
        self._currentStepIndex:    int                        = 0

        self._umlPubSubEngine:  UmlPubSubEngine   = UmlPubSubEngine()
        self._extensionsFacade: ExtensionsFacade  = ExtensionsFacade()
        self._hiddenDiagram:    ClassDiagramFrame = ClassDiagramFrame(
            parent=self,
            umlPubSubEngine=self._umlPubSubEngine,
        )
        self._hiddenDiagram.Hide()

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

        self._prevButton: Button = Button(toolbarPanel, ID_ANY, '< Prev')
        self._prevButton.SetSizerProps(valign='center')
        self._prevButton.Bind(EVT_BUTTON, self.onPrevStep)

        self._nextButton: Button = Button(toolbarPanel, ID_ANY, 'Next >')
        self._nextButton.SetSizerProps(valign='center')
        self._nextButton.Bind(EVT_BUTTON, self.onNextStep)

        self._resetButton: Button = Button(toolbarPanel, ID_ANY, 'Reset')
        self._resetButton.SetSizerProps(valign='center')
        self._resetButton.Bind(EVT_BUTTON, self.onReset)

        self._levelBandsCheck: CheckBox = CheckBox(toolbarPanel, ID_ANY, 'Level Bands')
        self._levelBandsCheck.SetValue(True)
        self._levelBandsCheck.SetSizerProps(valign='center')
        self._levelBandsCheck.Bind(EVT_CHECKBOX, self.onOverlayChanged)

        self._virtualNodesCheck: CheckBox = CheckBox(toolbarPanel, ID_ANY, 'Virtual Nodes')
        self._virtualNodesCheck.SetValue(True)
        self._virtualNodesCheck.SetSizerProps(valign='center')
        self._virtualNodesCheck.Bind(EVT_CHECKBOX, self.onOverlayChanged)

        self._barycenterCheck: CheckBox = CheckBox(toolbarPanel, ID_ANY, 'Barycenter')
        self._barycenterCheck.SetValue(True)
        self._barycenterCheck.SetSizerProps(valign='center')
        self._barycenterCheck.Bind(EVT_CHECKBOX, self.onOverlayChanged)

        self._controlPointsCheck: CheckBox = CheckBox(toolbarPanel, ID_ANY, 'Control Points')
        self._controlPointsCheck.SetValue(True)
        self._controlPointsCheck.SetSizerProps(valign='center')
        self._controlPointsCheck.Bind(EVT_CHECKBOX, self.onOverlayChanged)

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
        Load a preset dataset, run the Sugiyama stepper, and display Step 0.

        Args:
            index: Index into self._dataSets.
        """
        if index < 0 or index >= len(self._dataSets):
            return

        self._currentDataSetIndex = index
        dataSet: SugiyamaDataSet  = self._dataSets[index]
        stepper: SugiyamaStepper  = SugiyamaStepper(
            dataSet=dataSet,
            diagramFrame=self._hiddenDiagram,
            extensionsFacade=self._extensionsFacade,
        )
        self._steps = stepper.steps
        self._currentStepIndex = 0
        self._applyCurrentStep()

    def _applyCurrentStep(self):
        """
        Render the active step snapshot and update toolbar, inspector, and status bar.
        """
        if len(self._steps) == 0:
            return

        snapshot: SugiyamaStepSnapshot = self._steps[self._currentStepIndex]
        dataSet:  SugiyamaDataSet      = self._dataSets[self._currentDataSetIndex]

        self._canvasPanel.setOverlayOptions(
            showLevelBands=self._levelBandsCheck.GetValue(),
            showVirtualNodes=self._virtualNodesCheck.GetValue(),
            showBarycenterLabels=self._barycenterCheck.GetValue(),
            showControlPoints=self._controlPointsCheck.GetValue(),
        )
        self._canvasPanel.renderStep(snapshot)
        self._inspectorPanel.showStep(snapshot, len(self._steps), dataSet.name)

        self._prevButton.Enable(self._currentStepIndex > 0)
        self._nextButton.Enable(self._currentStepIndex < len(self._steps) - 1)

        self._statusBar.SetStatusText(
            f'{dataSet.name} | Crossings: {snapshot.crossingCount} | Virtual: {snapshot.virtualNodeCount}',
            0
        )
        self._statusBar.SetStatusText(
            f'Step {snapshot.stepIndex}/{len(self._steps) - 1}: {snapshot.phaseName}',
            1
        )

    def onPresetChanged(self, _event: CommandEvent):
        """
        Handle preset selection changes.

        Args:
            _event: Choice selection event.
        """
        index: int = self._presetChoice.GetSelection()
        self._loadDataSet(index)

    def onPrevStep(self, _event: CommandEvent):
        """
        Step backward to the previous Sugiyama phase.

        Args:
            _event: Button click event.
        """
        if self._currentStepIndex > 0:
            self._currentStepIndex -= 1
            self._applyCurrentStep()

    def onNextStep(self, _event: CommandEvent):
        """
        Step forward to the next Sugiyama phase.

        Args:
            _event: Button click event.
        """
        if self._currentStepIndex < len(self._steps) - 1:
            self._currentStepIndex += 1
            self._applyCurrentStep()

    def onReset(self, _event: CommandEvent):
        """
        Reset the active preset to Step 0.

        Args:
            _event: Button click event.
        """
        self._currentStepIndex = 0
        self._applyCurrentStep()

    def onOverlayChanged(self, _event: CommandEvent):
        """
        Re-render the active step when an overlay checkbox is toggled.

        Args:
            _event: Checkbox toggle event.
        """
        self._applyCurrentStep()
