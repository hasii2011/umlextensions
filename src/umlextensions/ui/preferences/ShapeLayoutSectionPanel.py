
from typing import cast

from logging import Logger
from logging import getLogger

from wx import CommandEvent
from wx import EVT_SPINCTRL
from wx import EVT_TEXT
from wx import ID_ANY
from wx import SpinCtrl
from wx import StaticText
from wx import Window

from wx.lib.sized_controls import SizedStaticBox

from umlextensions.ExtensionsPreferences import ExtensionsPreferences
from umlextensions.ui.preferences.BaseExtPreferencesPanel import BaseExtPreferencesPanel


class ShapeLayoutSectionPanel(BaseExtPreferencesPanel):
    """
    Preferences panel for the 'Shape Layout' INI section.

    Covers:
        startX      - SpinCtrl
        startY      - SpinCtrl
        xIncrement  - SpinCtrl
        maximumX    - SpinCtrl

    Reuses the BaseConfigPanel._layoutFormControls() infrastructure for
    consistent form layout with labels and spin controls.
    """

    PANEL_NAME: str = 'Shape Layout'

    def __init__(self, parent: Window):

        super().__init__(parent)

        self.logger: Logger = getLogger(__name__)

        self.SetSizerType('vertical')

        self._startXCtrl:     SpinCtrl = cast(SpinCtrl, None)   # noqa
        self._startYCtrl:     SpinCtrl = cast(SpinCtrl, None)   # noqa
        self._xIncrementCtrl: SpinCtrl = cast(SpinCtrl, None)   # noqa
        self._maximumXCtrl:   SpinCtrl = cast(SpinCtrl, None)   # noqa

        self._layoutControls()
        self._setControlValues()

    @property
    def name(self) -> str:
        return ShapeLayoutSectionPanel.PANEL_NAME

    def _layoutControls(self):

        layoutBox: SizedStaticBox = SizedStaticBox(self, ID_ANY, 'Shape Placement')
        layoutBox.SetSizerType('form')
        layoutBox.SetSizerProps(expand=True)

        st1: StaticText = StaticText(layoutBox, ID_ANY, 'Start X')
        st1.SetSizerProps(valign='center')
        self._startXCtrl = SpinCtrl(layoutBox, ID_ANY, min=0, max=10000)
        self._startXCtrl.SetSizerProps(expand=True, valign='center')
        self._startXCtrl.SetToolTip('Initial X coordinate for the first shape placed on the canvas')
        self.Bind(EVT_SPINCTRL, self._onStartXChanged, self._startXCtrl)
        self.Bind(EVT_TEXT,     self._onStartXChanged, self._startXCtrl)

        st2: StaticText = StaticText(layoutBox, ID_ANY, 'Start Y')
        st2.SetSizerProps(valign='center')
        self._startYCtrl = SpinCtrl(layoutBox, ID_ANY, min=0, max=10000)
        self._startYCtrl.SetSizerProps(expand=True, valign='center')
        self._startYCtrl.SetToolTip('Initial Y coordinate for the first shape placed on the canvas')
        self.Bind(EVT_SPINCTRL, self._onStartYChanged, self._startYCtrl)
        self.Bind(EVT_TEXT,     self._onStartYChanged, self._startYCtrl)

        st3: StaticText = StaticText(layoutBox, ID_ANY, 'X Increment')
        st3.SetSizerProps(valign='center')
        self._xIncrementCtrl = SpinCtrl(layoutBox, ID_ANY, min=0, max=10000)
        self._xIncrementCtrl.SetSizerProps(expand=True, valign='center')
        self._xIncrementCtrl.SetToolTip('Horizontal spacing between automatically placed shapes')
        self.Bind(EVT_SPINCTRL, self._onXIncrementChanged, self._xIncrementCtrl)
        self.Bind(EVT_TEXT,     self._onXIncrementChanged, self._xIncrementCtrl)

        st4: StaticText = StaticText(layoutBox, ID_ANY, 'Maximum X')
        st4.SetSizerProps(valign='center')
        self._maximumXCtrl = SpinCtrl(layoutBox, ID_ANY, min=100, max=10000)
        self._maximumXCtrl.SetSizerProps(expand=True, valign='center')
        self._maximumXCtrl.SetToolTip('Maximum X coordinate; shapes wrap to the next row when this value is reached')
        self.Bind(EVT_SPINCTRL, self._onMaximumXChanged, self._maximumXCtrl)
        self.Bind(EVT_TEXT,     self._onMaximumXChanged, self._maximumXCtrl)

    def _setControlValues(self):
        p: ExtensionsPreferences = self._preferences
        self._startXCtrl.SetValue(p.startX)
        self._startYCtrl.SetValue(p.startY)
        self._xIncrementCtrl.SetValue(p.xIncrement)
        self._maximumXCtrl.SetValue(p.maximumX)

    def _onStartXChanged(self, event: CommandEvent):
        self._preferences.startX = event.GetInt()

    def _onStartYChanged(self, event: CommandEvent):
        self._preferences.startY = event.GetInt()

    def _onXIncrementChanged(self, event: CommandEvent):
        self._preferences.xIncrement = event.GetInt()

    def _onMaximumXChanged(self, event: CommandEvent):
        self._preferences.maximumX = event.GetInt()
