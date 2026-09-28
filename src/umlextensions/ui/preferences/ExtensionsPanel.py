
from typing import cast

from logging import Logger
from logging import getLogger

from wx import ID_ANY
from wx import EVT_TEXT
from wx import DefaultCoord
from wx import EVT_CHECKBOX

from wx import Size
from wx import Window
from wx import CheckBox
from wx import TextCtrl
from wx import StaticText
from wx import CommandEvent

from wx.lib.sized_controls import SizedStaticBox

from codeallybasic.Dimensions import Dimensions

from codeallyadvanced.ui.widgets.DimensionsControl import DimensionsControl
from codeallyadvanced.ui.widgets.DimensionsControl import DimensionsParameters
from codeallyadvanced.ui.widgets.PositionControl import PositionControl
from codeallyadvanced.ui.widgets.PositionControl import PositionParameters

from umlshapes.types.UmlPosition import UmlPosition

from umlextensions.ExtensionsPreferences import ExtensionsPreferences
from umlextensions.ui.preferences.BasePreferencesPanel import BasePreferencesPanel

GML_BOX_MIN_HEIGHT:  int = 60
UNCONSTRAINED_WIDTH: int = DefaultCoord
LAYOUT_SIZE_MIN:     int = 64
LAYOUT_SIZE_MAX:     int = 8192


class ExtensionsPanel(BasePreferencesPanel):
    """
    Preferences panel for the 'Extensions' INI section.

    Covers:
        sugiyamaStepByStep      - CheckBox
        defaultGMLFilename      - TextCtrl
        orthogonalLayoutSize    - DimensionsControl
        orthogonalLayoutTopLeft - PositionControl
    """

    PANEL_NAME: str = 'Extensions'

    def __init__(self, parent: Window):

        super().__init__(parent)

        self.logger: Logger = getLogger(__name__)

        self.SetSizerType('vertical')

        self._sugiyamaStepByStep:      CheckBox          = cast(CheckBox,          None)     # noqa
        self._defaultGMLFilename:      TextCtrl          = cast(TextCtrl,          None)     # noqa
        self._layoutDimensionsControl: DimensionsControl = cast(DimensionsControl, None)     # noqa
        self._topLeftControl:          PositionControl   = cast(PositionControl,   None)     # noqa

        self._layoutControls()
        self._setControlValues()

    @property
    def name(self) -> str:
        return ExtensionsPanel.PANEL_NAME

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
        gmlBox.SetMinSize(Size(UNCONSTRAINED_WIDTH, GML_BOX_MIN_HEIGHT))
        gmlBox.SetSizerProps(expand=True)

        st: StaticText = StaticText(gmlBox, ID_ANY, 'Filename')
        st.SetSizerProps(valign='center')
        self._defaultGMLFilename = TextCtrl(gmlBox, ID_ANY)
        self._defaultGMLFilename.SetSizerProps(expand=True, valign='center')
        self._defaultGMLFilename.SetToolTip('Default filename used when dumping GML output')
        self.Bind(EVT_TEXT, self._onDefaultGMLFilenameChanged, self._defaultGMLFilename)

    def _layoutOrthogonalLayoutSize(self):
        """
        Lays out the orthogonal layout area dimensions control.
        """
        dimensionsParameters: DimensionsParameters = DimensionsParameters(
            caption='Orthogonal Layout Size',
            firstSpinnerLabel='Width:',
            secondSpinnerLabel='Height:',
            minValue=LAYOUT_SIZE_MIN,
            maxValue=LAYOUT_SIZE_MAX,
            valueChangedCallback=self._onLayoutSizeChanged,
        )
        self._layoutDimensionsControl = DimensionsControl(parent=self, parameters=dimensionsParameters)
        self._layoutDimensionsControl.SetSizerProps(expand=True)

    def _layoutOrthogonalLayoutTopLeft(self):
        """
        Lays out the orthogonal layout top-left position control.
        """
        positionParameters: PositionParameters = PositionParameters(
            caption='Orthogonal Layout Top-Left',
            minValue=0,
            maxValue=8192,
            valueChangedCallback=self._onTopLeftChanged,
        )
        self._topLeftControl = PositionControl(parent=self, parameters=positionParameters)
        self._topLeftControl.SetSizerProps(expand=True)

    def _setControlValues(self):

        p: ExtensionsPreferences = self._preferences

        self._sugiyamaStepByStep.SetValue(p.sugiyamaStepByStep)
        self._defaultGMLFilename.SetValue(p.defaultGMLFilename)

        layoutSize: Dimensions = p.orthogonalLayoutSize
        self._layoutDimensionsControl.dimensions = layoutSize

        topLeft: UmlPosition = p.orthogonalLayoutTopLeft
        self._topLeftControl.position = topLeft

    # ── Event Handlers ───────────────────────────────────────────────────────

    def _onSugiyamaStepByStepChanged(self, event: CommandEvent):
        self._preferences.sugiyamaStepByStep = event.IsChecked()

    def _onDefaultGMLFilenameChanged(self, event: CommandEvent):
        self._preferences.defaultGMLFilename = event.GetString()

    def _onLayoutSizeChanged(self, newDimensions: Dimensions):
        self._preferences.orthogonalLayoutSize = newDimensions

    def _onTopLeftChanged(self, newPosition: UmlPosition):
        self._preferences.orthogonalLayoutTopLeft = newPosition
