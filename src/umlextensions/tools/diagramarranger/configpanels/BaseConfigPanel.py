
from logging import Logger
from logging import getLogger

from wx import EVT_CHECKBOX
from wx import ID_ANY
from wx import EVT_TEXT
from wx import EVT_SPINCTRL
from wx import EVT_SPINCTRLDOUBLE

from wx import Window
from wx import CheckBox
from wx import SpinCtrl
from wx import StaticText
from wx import SpinCtrlDouble

from wx.lib.sized_controls import SizedPanel

from codeallybasic.Position import Position

from umlextensions.ExtensionsPreferences import ExtensionsPreferences
from umlextensions.tools.diagramarranger.configpanels.ValueControlSpec import ControlType
from umlextensions.tools.diagramarranger.configpanels.ValueControlSpec import UnknownControlType

from umlextensions.tools.diagramarranger.configpanels.ValueControlSpec import ValueControlSpecs

from codeallyadvanced.ui.widgets.PositionControl import PositionControl
"""
    These are not preferences,  just some of my arbitrary values
"""
MIN_LAYOUT_CENTER: int = 100
MAX_LAYOUT_CENTER: int = 10000


class BaseConfigPanel(SizedPanel):
    """
    Parent panel for the Diagram Arranger configuration panels
    """

    def __init__(self, parent: Window):
        """

        Args:
            parent:     The parent window
        """

        super().__init__(parent)

        self.bLogger: Logger = getLogger(__name__)

        self._preferences: ExtensionsPreferences = ExtensionsPreferences()

    def _layoutFormControls(self, formPanel: SizedPanel, valueControlSpecs: ValueControlSpecs):
        """
        Assumes that this sized panel is a 'form'  lays out the  controls assuming that they
        are either a regular spinner or a float spinner

        It sets the specific 'change' callback to respond to either a spinner event or a text
        event (user types in new value)


        Args:
            formPanel            The parent panel for the controls
            valueControlSpecs:   The descriptions of the controls to layout

        """
        for valueControlSpec in valueControlSpecs:

            sText = StaticText(formPanel, ID_ANY, valueControlSpec.valueLabel)
            sText.SetSizerProps(valign='center')
            sText.SetToolTip(valueControlSpec.toolTip)

            if valueControlSpec.controlType == ControlType.SPIN_CTRL_DOUBLE:
                valueControlSpec.valueCtrl = SpinCtrlDouble(
                    formPanel,
                    initial=valueControlSpec.initialValue,
                    min=valueControlSpec.minValue,
                    max=valueControlSpec.maxValue
                )
                valueControlSpec.valueCtrl.SetDigits(valueControlSpec.floatDigits)  # noqa
                self.Bind(EVT_SPINCTRLDOUBLE, valueControlSpec.spinCallback, valueControlSpec.valueCtrl)
                valueControlSpec.valueCtrl.SetIncrement(valueControlSpec.spinnerIncrement)

            elif valueControlSpec.controlType == ControlType.SPIN_CTRL:
                valueControlSpec.valueCtrl = SpinCtrl(
                    formPanel,
                    initial=valueControlSpec.initialValue,  # noqa
                    min=valueControlSpec.minValue,
                    max=valueControlSpec.maxValue
                )
                self.Bind(EVT_SPINCTRL, valueControlSpec.spinCallback, valueControlSpec.valueCtrl)
                if valueControlSpec.textCallback is not None:
                    self.Bind(EVT_TEXT, valueControlSpec.textCallback, valueControlSpec.valueCtrl)
                else:
                    self.bLogger.warning(f'No text callback registered for {valueControlSpec.valueLabel}')
                valueControlSpec.valueCtrl.SetIncrement(valueControlSpec.spinnerIncrement)
            elif valueControlSpec.controlType == ControlType.CHECK_BOX:

                valueControlSpec.valueCtrl = CheckBox(formPanel,ID_ANY, '')
                valueControlSpec.valueCtrl.SetValue(valueControlSpec.initialValue)

                self.Bind(EVT_CHECKBOX, valueControlSpec.checkBoxCallback, valueControlSpec.valueCtrl)
            else:
                raise UnknownControlType(f'{valueControlSpec.controlType.value}')


            valueControlSpec.valueCtrl.SetSizerProps(expand=True, valign='center')
            valueControlSpec.valueCtrl.SetToolTip(valueControlSpec.toolTip)

    def _layoutTheDiagramCenter(self, sizedPanel: SizedPanel, p: ExtensionsPreferences) -> PositionControl:
        """
        Creates a position control.  Used by configuration panels to change the center of the UML
        Diagram once the tools executes the appropriate layout algorithm

        Args:
            sizedPanel:     Where we live in
            p:              Preferences object

        Returns:  The created position control;  It is up to the caller to set the
        appropriate sizer properties to make it appear aesthetically pleasing in the
        parent container
        """

        layoutCenter: PositionControl = PositionControl(
            sizedPanel=sizedPanel,
            displayText='Layout Center',
            minValue=MIN_LAYOUT_CENTER,
            maxValue=MAX_LAYOUT_CENTER,
            valueChangedCallback=self._layoutCenterChanged,
            setControlsSize=True
        )
        layoutCenter.position = p.layoutCenter
        layoutCenter.SetToolTip('The coordinate pair around which to center the layout')

        return layoutCenter

    def _layoutCenterChanged(self, newPosition: Position):
        self._preferences.layoutCenter = newPosition
