
from typing import cast

from logging import Logger
from logging import getLogger

from wx import ID_ANY
from wx import EVT_TEXT
from wx import EVT_SPINCTRL

from wx import Window
from wx import SpinCtrl
from wx import StaticText
from wx import CommandEvent
from wx import FlexGridSizer

from wx.lib.sized_controls import SizedStaticBox

from umlshapes.types.UmlPosition import UmlPosition

from codeallyadvanced.ui.widgets.PositionControl import PositionControl
from codeallyadvanced.ui.widgets.PositionControl import PositionParameters

from umlextensions.ExtensionsPreferences import ExtensionsPreferences
from umlextensions.input.python.InitialShapePosition import InitialShapePosition
from umlextensions.ui.preferences.BaseExtPreferencesPanel import BaseExtPreferencesPanel

FORM_ROW_GAP: int = 10
FORM_COL_GAP: int = 10


class ShapeLayoutSectionPanel(BaseExtPreferencesPanel):
    """
    Preferences panel for the 'Shape Layout' INI section.

    Covers:
        initialShapePosition - PositionControl
        xIncrement           - SpinCtrl
        maximumX             - SpinCtrl
    """

    PANEL_NAME: str = 'Shape Layout'

    def __init__(self, parent: Window):

        super().__init__(parent)

        self.logger: Logger = getLogger(__name__)

        self.SetSizerType('vertical')

        self._initialShapePositionControl: PositionControl = cast(PositionControl, None)   # noqa
        self._xIncrementCtrl:              SpinCtrl        = cast(SpinCtrl,        None)   # noqa
        self._maximumXCtrl:                SpinCtrl        = cast(SpinCtrl,        None)   # noqa

        self._layoutControls()
        self._setControlValues()

    @property
    def name(self) -> str:
        return ShapeLayoutSectionPanel.PANEL_NAME

    def _layoutControls(self):

        positionParameters: PositionParameters = PositionParameters(
            caption='Initial Shape Position',
            minValue=0,
            maxValue=10000,
            valueChangedCallback=self._onPositionChanged,
        )
        self._initialShapePositionControl = PositionControl(parent=self, parameters=positionParameters)
        self._initialShapePositionControl.SetSizerProps(expand=True)

        layoutBox: SizedStaticBox = SizedStaticBox(self, ID_ANY, 'Shape Placement')
        layoutBox.SetSizerType('form')
        layoutBox.SetSizerProps(expand=True)

        formSizer: FlexGridSizer = cast(FlexGridSizer, layoutBox.GetSizer())
        formSizer.SetVGap(FORM_ROW_GAP)
        formSizer.SetHGap(FORM_COL_GAP)

        st1: StaticText = StaticText(layoutBox, ID_ANY, 'X Increment')
        st1.SetSizerProps(valign='center')
        self._xIncrementCtrl = SpinCtrl(layoutBox, ID_ANY, min=0, max=10000)
        self._xIncrementCtrl.SetSizerProps(expand=True, valign='center')
        self._xIncrementCtrl.SetToolTip('Horizontal spacing between automatically placed shapes')
        self.Bind(EVT_SPINCTRL, self._onXIncrementChanged, self._xIncrementCtrl)
        self.Bind(EVT_TEXT,     self._onXIncrementChanged, self._xIncrementCtrl)

        st2: StaticText = StaticText(layoutBox, ID_ANY, 'Maximum X')
        st2.SetSizerProps(valign='center')
        self._maximumXCtrl = SpinCtrl(layoutBox, ID_ANY, min=100, max=10000)
        self._maximumXCtrl.SetSizerProps(expand=True, valign='center')
        self._maximumXCtrl.SetToolTip('Maximum X coordinate; shapes wrap to the next row when this value is reached')
        self.Bind(EVT_SPINCTRL, self._onMaximumXChanged, self._maximumXCtrl)
        self.Bind(EVT_TEXT,     self._onMaximumXChanged, self._maximumXCtrl)

    def _setControlValues(self):
        p: ExtensionsPreferences = self._preferences

        initialPosition: InitialShapePosition = p.initialShapePosition
        self._initialShapePositionControl.position = initialPosition
        self._xIncrementCtrl.SetValue(p.xIncrement)
        self._maximumXCtrl.SetValue(p.maximumX)

    def _onPositionChanged(self, newPosition: UmlPosition):
        self._preferences.initialShapePosition = InitialShapePosition(x=newPosition.x, y=newPosition.y)

    def _onXIncrementChanged(self, event: CommandEvent):
        self._preferences.xIncrement = event.GetInt()

    def _onMaximumXChanged(self, event: CommandEvent):
        self._preferences.maximumX = event.GetInt()
