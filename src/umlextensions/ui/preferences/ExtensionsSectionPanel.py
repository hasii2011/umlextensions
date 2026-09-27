
from typing import cast

from logging import Logger
from logging import getLogger

from wx import EVT_CHECKBOX
from wx import EVT_SPINCTRL
from wx import EVT_TEXT
from wx import ID_ANY

from wx import CheckBox
from wx import CommandEvent
from wx import SpinCtrl
from wx import StaticText
from wx import TextCtrl
from wx import Window

from wx.lib.sized_controls import SizedStaticBox

from codeallyadvanced.ui.widgets.PositionControl import PositionControl

from umlshapes.types.UmlPosition import UmlPosition

from umlextensions.tools.orthogonallayout.LayoutAreaDimensions import LayoutAreaDimensions
from umlextensions.ExtensionsPreferences import ExtensionsPreferences
from umlextensions.ui.preferences.BaseExtPreferencesPanel import BaseExtPreferencesPanel

LAYOUT_SIZE_MIN: int = 64
LAYOUT_SIZE_MAX: int = 8192


class ExtensionsSectionPanel(BaseExtPreferencesPanel):
    """
    Preferences panel for the 'Extensions' INI section.

    Covers:
        sugiyamaStepByStep      - CheckBox
        defaultGMLFilename      - TextCtrl
        orthogonalLayoutSize    - Two SpinCtrl (width x height)
        orthogonalLayoutTopLeft - PositionControl
    """

    PANEL_NAME: str = 'Extensions'

    def __init__(self, parent: Window):

        super().__init__(parent)

        self.logger: Logger = getLogger(__name__)

        self.SetSizerType('vertical')

        self._sugiyamaStepByStep: CheckBox  = cast(CheckBox,  None)                 # noqa
        self._defaultGMLFilename: TextCtrl  = cast(TextCtrl,  None)                 # noqa
        self._layoutWidth:        SpinCtrl  = cast(SpinCtrl,  None)                 # noqa
        self._layoutHeight:       SpinCtrl  = cast(SpinCtrl,  None)                 # noqa
        self._topLeftControl:     PositionControl = cast(PositionControl, None)     # noqa

        self._layoutControls()
        self._setControlValues()

    @property
    def name(self) -> str:
        return ExtensionsSectionPanel.PANEL_NAME

    def _layoutControls(self):
        """
        Builds and lays out the preference controls for the extensions section.
        """
        self._layoutSugiyamaStepByStep()
        self._layoutDefaultGmlFilename()
        self._layoutOrthogonalLayoutSize()
        self._layoutOrthogonalLayoutTopLeft()

    def _layoutSugiyamaStepByStep(self):
        """
        Lays out the Sugiyama step-by-step execution checkbox.
        """
        self._sugiyamaStepByStep = CheckBox(self, ID_ANY, 'Sugiyama Step By Step')
        self._sugiyamaStepByStep.SetToolTip('Run the Sugiyama layout one step at a time for debugging')
        self.Bind(EVT_CHECKBOX, self._onSugiyamaStepByStepChanged, self._sugiyamaStepByStep)

    def _layoutDefaultGmlFilename(self):
        """
        Lays out the default GML filename input box.
        """
        gmlBox: SizedStaticBox = SizedStaticBox(self, ID_ANY, 'Default GML Filename')
        gmlBox.SetSizerType('form')
        gmlBox.SetSizerProps(expand=True)

        StaticText(gmlBox, ID_ANY, 'Filename')
        self._defaultGMLFilename = TextCtrl(gmlBox, ID_ANY)
        self._defaultGMLFilename.SetSizerProps(expand=True)
        self._defaultGMLFilename.SetToolTip('Default filename used when dumping GML output')
        self.Bind(EVT_TEXT, self._onDefaultGMLFilenameChanged, self._defaultGMLFilename)

    def _layoutOrthogonalLayoutSize(self):
        """
        Lays out the orthogonal layout area dimensions input box.
        """
        sizeBox: SizedStaticBox = SizedStaticBox(self, ID_ANY, 'Orthogonal Layout Size')
        sizeBox.SetSizerType('form')
        sizeBox.SetSizerProps(expand=True)

        StaticText(sizeBox, ID_ANY, 'Width')
        self._layoutWidth = SpinCtrl(sizeBox, ID_ANY, min=LAYOUT_SIZE_MIN, max=LAYOUT_SIZE_MAX)
        self._layoutWidth.SetSizerProps(expand=True)
        self._layoutWidth.SetToolTip('Width of the orthogonal layout area in pixels')
        self.Bind(EVT_SPINCTRL, self._onLayoutWidthChanged, self._layoutWidth)
        self.Bind(EVT_TEXT,     self._onLayoutWidthChanged, self._layoutWidth)

        StaticText(sizeBox, ID_ANY, 'Height')
        self._layoutHeight = SpinCtrl(sizeBox, ID_ANY, min=LAYOUT_SIZE_MIN, max=LAYOUT_SIZE_MAX)
        self._layoutHeight.SetSizerProps(expand=True)
        self._layoutHeight.SetToolTip('Height of the orthogonal layout area in pixels')
        self.Bind(EVT_SPINCTRL, self._onLayoutHeightChanged, self._layoutHeight)
        self.Bind(EVT_TEXT,     self._onLayoutHeightChanged, self._layoutHeight)

    def _layoutOrthogonalLayoutTopLeft(self):
        """
        Lays out the orthogonal layout top-left position control.
        """
        self._topLeftControl = PositionControl(
            sizedPanel=self,
            displayText='Orthogonal Layout Top-Left',
            minValue=0,
            maxValue=8192,
            valueChangedCallback=self._onTopLeftChanged,
            setControlsSize=True
        )
        self._topLeftControl.SetSizerProps(expand=True)

    def _setControlValues(self):

        p: ExtensionsPreferences = self._preferences

        self._sugiyamaStepByStep.SetValue(p.sugiyamaStepByStep)
        self._defaultGMLFilename.SetValue(p.defaultGMLFilename)

        layoutSize: LayoutAreaDimensions = p.orthogonalLayoutSize
        self._layoutWidth.SetValue(layoutSize.width)
        self._layoutHeight.SetValue(layoutSize.height)

        topLeft: UmlPosition = p.orthogonalLayoutTopLeft
        self._topLeftControl.position = topLeft

    # ── Event Handlers ───────────────────────────────────────────────────────

    def _onSugiyamaStepByStepChanged(self, event: CommandEvent):
        self._preferences.sugiyamaStepByStep = event.IsChecked()

    def _onDefaultGMLFilenameChanged(self, event: CommandEvent):
        self._preferences.defaultGMLFilename = event.GetString()

    def _onLayoutWidthChanged(self, event: CommandEvent):
        currentSize: LayoutAreaDimensions = self._preferences.orthogonalLayoutSize
        currentSize.width = event.GetInt()
        self._preferences.orthogonalLayoutSize = currentSize

    def _onLayoutHeightChanged(self, event: CommandEvent):
        currentSize: LayoutAreaDimensions = self._preferences.orthogonalLayoutSize
        currentSize.height = event.GetInt()
        self._preferences.orthogonalLayoutSize = currentSize

    def _onTopLeftChanged(self, newPosition: UmlPosition):
        self._preferences.orthogonalLayoutTopLeft = newPosition
