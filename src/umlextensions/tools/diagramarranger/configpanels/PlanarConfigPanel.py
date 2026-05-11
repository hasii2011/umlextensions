
from wx import Window
from wx import CommandEvent

from wx.lib.sized_controls import SizedPanel

from codeallyadvanced.ui.widgets.PositionControl import PositionControl

from umlextensions.Common import createBalloonTip
from umlextensions.ExtensionsPreferences import ExtensionsPreferences

from umlextensions.tools.diagramarranger.configpanels.BaseConfigPanel import BaseConfigPanel
from umlextensions.tools.diagramarranger.configpanels.ValueControlSpec import ControlType
from umlextensions.tools.diagramarranger.configpanels.ValueControlSpec import ValueControlSpecs
from umlextensions.tools.diagramarranger.configpanels.ValueControlSpec import ValueControlSpec


class PlanarConfigPanel(BaseConfigPanel):
    TIP_TITLE: str = 'Planar layout algorithm'
    TIP_TEXT: str = """
    Position shapes that minimizes line intersections.
    """

    def __init__(self, parent: Window):

        super().__init__(parent)

        self.SetSizerType('vertical')

        self._layoutControls(parent=self, p=self._preferences)

        createBalloonTip(
            tipTitle=PlanarConfigPanel.TIP_TITLE,
            tipText=PlanarConfigPanel.TIP_TEXT,
            tipTarget=self._layoutHelpButton(self)
        )

    def _layoutControls(self, parent: SizedPanel, p: ExtensionsPreferences):
        """
        The underlying methods not only do the layout the set the control values and
        bind the event handlers

        Args:
            parent:  The parent panel
            p:       The preferences
        """

        pc: PositionControl = self._layoutTheDiagramCenter(sizedPanel=parent, p=p)
        pc.SetSizerProps(proportion=1)
        innerForm: SizedPanel = SizedPanel(parent=parent)
        innerForm.SetSizerType('form')
        innerForm.SetSizerProps(proportion=2)

        valueControlSpecs: ValueControlSpecs = ValueControlSpecs(
            [
                ValueControlSpec(
                    valueLabel='Positions Scale',
                    spinCallback=self._onPositionScaleChanged,
                    textCallback=self._onPositionScaleChanged,
                    initialValue=p.positionsScale,
                    controlType=ControlType.SPIN_CTRL,
                    toolTip='Scale factor for positions.'
                ),
                ValueControlSpec(
                    valueLabel='Frame Scale Factor',
                    spinCallback=self._onFrameScaleFactorChanged,
                    textCallback=self._onFrameScaleFactorChanged,
                    initialValue=p.planarFrameScaleFactor,
                    controlType=ControlType.SPIN_CTRL,
                    toolTip='Factor that adjusts the layout to the UML Frame size.'
                ),
            ]
        )
        self._layoutFormControls(valueControlSpecs=valueControlSpecs, formPanel=innerForm)

    def _onPositionScaleChanged(self, event: CommandEvent):
        newValue: int = event.GetInt()
        self._preferences.positionsScale = newValue

    def _onFrameScaleFactorChanged(self, event: CommandEvent):
        newValue: int = event.GetInt()
        self._preferences.planarFrameScaleFactor = newValue
