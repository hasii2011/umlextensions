
from typing import cast

from logging import Logger
from logging import getLogger

from wx import ID_ANY
from wx import EVT_TEXT
from wx import EVT_SPINCTRL
from wx import EVT_CHECKBOX

from wx import Size
from wx import Window
from wx import CheckBox
from wx import SpinCtrl
from wx import StaticText
from wx import CommandEvent
from wx import FlexGridSizer

from wx.lib.sized_controls import SizedStaticBox

from umlextensions.tools.sugiyama.SugiyamaPreferences import SugiyamaPreferences
from umlextensions.ui.preferences.BasePreferencesPanel import BasePreferencesPanel

FORM_ROW_GAP:             int = 8
FORM_COL_GAP:             int = 12
BOX_BORDER:               int = 8
SPINNER_WIDTH:            int = 90
MARGINS_BOX_MIN_HEIGHT:   int = 95
SPACING_BOX_MIN_HEIGHT:   int = 95
EXECUTION_BOX_MIN_HEIGHT: int = 60
MIN_MARGIN:               int = 0
MAX_MARGIN:               int = 1000
MIN_SPACE:                int = 0
MAX_SPACE:                int = 1000

TOOLTIP_LEFT_MARGIN:         str = 'Starting horizontal margin in pixels for leftmost shapes'
TOOLTIP_TOP_MARGIN:          str = 'Starting vertical margin in pixels for top-level shapes'
TOOLTIP_HORIZONTAL_SPACING: str = 'Minimum horizontal clearance in pixels between adjacent nodes in a level'
TOOLTIP_VERTICAL_SPACING:   str = 'Minimum vertical clearance in pixels between hierarchy levels'
TOOLTIP_STEP_BY_STEP:        str = 'Run the Sugiyama layout one step at a time for interactive debugging'


class SugiyamaPanel(BasePreferencesPanel):
    """
    Preferences panel for the Sugiyama automatic layout algorithm.

    Covers:
        leftMargin         - SpinCtrl
        topMargin          - SpinCtrl
        horizontalSpacing  - SpinCtrl
        verticalSpacing    - SpinCtrl
        sugiyamaStepByStep - CheckBox
    """

    PANEL_NAME: str = 'Sugiyama'

    def __init__(self, parent: Window):

        super().__init__(parent)

        self.logger: Logger = getLogger(__name__)

        self.SetSizerType('vertical')

        self._sugiyamaPreferences: SugiyamaPreferences = SugiyamaPreferences()

        self._leftMarginCtrl:         SpinCtrl = cast(SpinCtrl, None)  # noqa
        self._topMarginCtrl:          SpinCtrl = cast(SpinCtrl, None)  # noqa
        self._horizontalSpacingCtrl: SpinCtrl = cast(SpinCtrl, None)  # noqa
        self._verticalSpacingCtrl:   SpinCtrl = cast(SpinCtrl, None)  # noqa
        self._stepByStepCtrl:         CheckBox = cast(CheckBox, None)  # noqa

        self._layoutControls()
        self._setControlValues()

    @property
    def name(self) -> str:
        return SugiyamaPanel.PANEL_NAME

    def _layoutControls(self):
        """
        Builds and lays out the preference controls for the Sugiyama layout algorithm.
        """
        self._layoutMarginsBox()
        self._layoutSpacingBox()
        self._layoutExecutionBox()

    def _layoutMarginsBox(self):
        """
        Lays out the canvas margins controls.
        """
        marginsBox: SizedStaticBox = SizedStaticBox(self, ID_ANY, 'Canvas Margins')
        marginsBox.SetSizerType('form')
        marginsBox.SetMinSize(Size(-1, MARGINS_BOX_MIN_HEIGHT))
        marginsBox.SetSizerProps(expand=True, border=(('all',), BOX_BORDER))

        formSizer: FlexGridSizer = cast(FlexGridSizer, marginsBox.GetSizer())
        formSizer.SetVGap(FORM_ROW_GAP)
        formSizer.SetHGap(FORM_COL_GAP)

        leftMarginLabel: StaticText = StaticText(marginsBox, ID_ANY, 'Left Margin')
        leftMarginLabel.SetSizerProps(valign='center')
        leftMarginLabel.SetToolTip(TOOLTIP_LEFT_MARGIN)
        self._leftMarginCtrl = SpinCtrl(marginsBox, ID_ANY, min=MIN_MARGIN, max=MAX_MARGIN, size=Size(SPINNER_WIDTH, -1))
        self._leftMarginCtrl.SetSizerProps(valign='center')
        self._leftMarginCtrl.SetToolTip(TOOLTIP_LEFT_MARGIN)
        self.Bind(EVT_SPINCTRL, self._onLeftMarginChanged, self._leftMarginCtrl)
        self.Bind(EVT_TEXT,     self._onLeftMarginChanged, self._leftMarginCtrl)

        topMarginLabel: StaticText = StaticText(marginsBox, ID_ANY, 'Top Margin')
        topMarginLabel.SetSizerProps(valign='center')
        topMarginLabel.SetToolTip(TOOLTIP_TOP_MARGIN)
        self._topMarginCtrl = SpinCtrl(marginsBox, ID_ANY, min=MIN_MARGIN, max=MAX_MARGIN, size=Size(SPINNER_WIDTH, -1))
        self._topMarginCtrl.SetSizerProps(valign='center')
        self._topMarginCtrl.SetToolTip(TOOLTIP_TOP_MARGIN)
        self.Bind(EVT_SPINCTRL, self._onTopMarginChanged, self._topMarginCtrl)
        self.Bind(EVT_TEXT,     self._onTopMarginChanged, self._topMarginCtrl)

    def _layoutSpacingBox(self):
        """
        Lays out the node and level spacing controls.
        """
        spacingBox: SizedStaticBox = SizedStaticBox(self, ID_ANY, 'Node & Level Spacing')
        spacingBox.SetSizerType('form')
        spacingBox.SetMinSize(Size(-1, SPACING_BOX_MIN_HEIGHT))
        spacingBox.SetSizerProps(expand=True, border=(('all',), BOX_BORDER))

        formSizer: FlexGridSizer = cast(FlexGridSizer, spacingBox.GetSizer())
        formSizer.SetVGap(FORM_ROW_GAP)
        formSizer.SetHGap(FORM_COL_GAP)

        horizontalSpacingLabel: StaticText = StaticText(spacingBox, ID_ANY, 'Horizontal Spacing')
        horizontalSpacingLabel.SetSizerProps(valign='center')
        horizontalSpacingLabel.SetToolTip(TOOLTIP_HORIZONTAL_SPACING)
        self._horizontalSpacingCtrl = SpinCtrl(spacingBox, ID_ANY, min=MIN_SPACE, max=MAX_SPACE, size=Size(SPINNER_WIDTH, -1))
        self._horizontalSpacingCtrl.SetSizerProps(valign='center')
        self._horizontalSpacingCtrl.SetToolTip(TOOLTIP_HORIZONTAL_SPACING)
        self.Bind(EVT_SPINCTRL, self._onHorizontalSpacingChanged, self._horizontalSpacingCtrl)
        self.Bind(EVT_TEXT,     self._onHorizontalSpacingChanged, self._horizontalSpacingCtrl)

        verticalSpacingLabel: StaticText = StaticText(spacingBox, ID_ANY, 'Vertical Spacing')
        verticalSpacingLabel.SetSizerProps(valign='center')
        verticalSpacingLabel.SetToolTip(TOOLTIP_VERTICAL_SPACING)
        self._verticalSpacingCtrl = SpinCtrl(spacingBox, ID_ANY, min=MIN_SPACE, max=MAX_SPACE, size=Size(SPINNER_WIDTH, -1))
        self._verticalSpacingCtrl.SetSizerProps(valign='center')
        self._verticalSpacingCtrl.SetToolTip(TOOLTIP_VERTICAL_SPACING)
        self.Bind(EVT_SPINCTRL, self._onVerticalSpacingChanged, self._verticalSpacingCtrl)
        self.Bind(EVT_TEXT,     self._onVerticalSpacingChanged, self._verticalSpacingCtrl)

    def _layoutExecutionBox(self):
        """
        Lays out execution mode controls (e.g. step-by-step debugging).
        """
        executionBox: SizedStaticBox = SizedStaticBox(self, ID_ANY, 'Execution Options')
        executionBox.SetSizerType('vertical')
        executionBox.SetMinSize(Size(-1, EXECUTION_BOX_MIN_HEIGHT))
        executionBox.SetSizerProps(expand=True, border=(('all',), BOX_BORDER))

        self._stepByStepCtrl = CheckBox(executionBox, ID_ANY, 'Sugiyama Step By Step')
        self._stepByStepCtrl.SetSizerProps(valign='center', border=(('all',), BOX_BORDER))
        self._stepByStepCtrl.SetToolTip(TOOLTIP_STEP_BY_STEP)
        self.Bind(EVT_CHECKBOX, self._onStepByStepChanged, self._stepByStepCtrl)

    def _setControlValues(self):
        p: SugiyamaPreferences = self._sugiyamaPreferences

        self._leftMarginCtrl.SetValue(p.leftMargin)
        self._topMarginCtrl.SetValue(p.topMargin)
        self._horizontalSpacingCtrl.SetValue(p.horizontalSpacing)
        self._verticalSpacingCtrl.SetValue(p.verticalSpacing)
        self._stepByStepCtrl.SetValue(p.sugiyamaStepByStep)

    def _onLeftMarginChanged(self, _event: CommandEvent):
        self._sugiyamaPreferences.leftMargin = self._leftMarginCtrl.GetValue()

    def _onTopMarginChanged(self, _event: CommandEvent):
        self._sugiyamaPreferences.topMargin = self._topMarginCtrl.GetValue()

    def _onHorizontalSpacingChanged(self, _event: CommandEvent):
        self._sugiyamaPreferences.horizontalSpacing = self._horizontalSpacingCtrl.GetValue()

    def _onVerticalSpacingChanged(self, _event: CommandEvent):
        self._sugiyamaPreferences.verticalSpacing = self._verticalSpacingCtrl.GetValue()

    def _onStepByStepChanged(self, _event: CommandEvent):
        stepByStepVal: bool = self._stepByStepCtrl.GetValue()
        self._sugiyamaPreferences.sugiyamaStepByStep = stepByStepVal
        self._preferences.sugiyamaStepByStep = stepByStepVal
