
from logging import Logger
from logging import getLogger

from wx import Choice

from wx import ID_ANY
from wx import EVT_CHOICE

from wx import Window
from wx import StaticText
from wx import CommandEvent
from wx import SpinDoubleEvent

from wx.lib.sized_controls import SizedPanel

from codeallyadvanced.ui.widgets.PositionControl import PositionControl

from umlextensions.Common import createBalloonTip
from umlextensions.ExtensionsPreferences import ExtensionsPreferences

from umlextensions.tools.diagramarranger.configpanels.BaseConfigPanel import BaseConfigPanel

from umlextensions.tools.diagramarranger.configpanels.ForceDirectedMethod import ForceDirectedMethod
from umlextensions.tools.diagramarranger.configpanels.ValueControlSpec import ControlType
from umlextensions.tools.diagramarranger.configpanels.ValueControlSpec import ValueControlSpecs
from umlextensions.tools.diagramarranger.configpanels.ValueControlSpec import ValueControlSpec


class SpringConfigPanel(BaseConfigPanel):

    TIP_TITLE: str = 'Spring Layout'
    TIP_TEXT: str = """  
    Applies a spring layout to the shapes in the provided UmlFrame.

    Position nodes using Fruchterman-Reingold force-directed algorithm.

    The algorithm simulates a force-directed representation of the network
    * It treats edges as springs holding the shapes close,
    * It treats the shapes as repelling objects, sometimes called an antigravity force.
    * The simulation continues until the positions are close to an equilibrium.
    """
    def __init__(self, parent: Window):
        """

        Args:
            parent:
        """

        super().__init__(parent)

        self.SetSizerType('vertical')

        self.logger: Logger = getLogger(__name__)

        self._layoutControls(parent=self, p=self._preferences)

        createBalloonTip(
            tipTitle=SpringConfigPanel.TIP_TITLE,
            tipText=SpringConfigPanel.TIP_TEXT,
            tipTarget=self._layoutHelpButton(self)
        )

    def _layoutControls(self, parent: SizedPanel, p: ExtensionsPreferences):
        """
        The underlying methods not only do the layout the set the control values and
        bind the event handlers

        Args:
            parent
            p:

        """

        pc: PositionControl = self._layoutTheDiagramCenter(sizedPanel=parent, p=p)
        pc.SetSizerProps(proportion=1)
        innerForm: SizedPanel = SizedPanel(parent=parent)
        innerForm.SetSizerType('form')
        innerForm.SetSizerProps(proportion=2)

        self._layoutNumericControls(formPanel=innerForm, p=p)
        self._layoutMethodChoice(formPanel=innerForm, p=p)

    def _layoutNumericControls(self, formPanel: SizedPanel, p: ExtensionsPreferences):
        """
        Assumes that this sized panel is a 'form'  lays out the following controls
            iterations
            scale factor
            optimal node distance

        Uses a table driven method for simplicity

        Args:
            formPanel
            p:  The short name for the preferences
        """
        valueControlSpecs: ValueControlSpecs = ValueControlSpecs(
                [
                    ValueControlSpec(
                        valueLabel='Iterations',
                        spinCallback=self._onIterationsChanged,
                        textCallback=self._onIterationsChanged,
                        initialValue=p.iterations,
                        controlType=ControlType.SPIN_CTRL,
                        toolTip='Number of iterations to execute'
                    ),
                    ValueControlSpec(
                        valueLabel='Frame Size Scale Factor',
                        spinCallback=self._onScaleFactorChange,
                        textCallback=self._onScaleFactorChange,
                        initialValue=p.frameSizeScaleFactor,
                        controlType=ControlType.SPIN_CTRL,
                        toolTip='Factor that adjusts the layout to the UML Frame size'
                    ),
                    ValueControlSpec(
                        valueLabel='Optimal Node Distance',
                        spinCallback=self._onNodeDistanceChange,
                        textCallback=self._onNodeDistanceChange,
                        initialValue=p.optimalNodeDistance,
                        controlType=ControlType.SPIN_CTRL_DOUBLE,
                        toolTip='Optimal distance between shapes; larger values space shapes farther apart'
                    ),
                ]
            )
        self._layoutFormControls(formPanel=formPanel, valueControlSpecs=valueControlSpecs)

    def _layoutMethodChoice(self, formPanel: SizedPanel, p: ExtensionsPreferences):
        """
        The algorithm to use

        Args:
            formPanel
            p:
        """

        sText = StaticText(formPanel, ID_ANY, 'Compute Method')
        sText.SetSizerProps(valign='center')
        sText.SetToolTip('If ‘auto’, we use ‘force’ if len(G) < 500 use ‘energy’.')

        layoutMethodChoice: Choice = Choice(
            formPanel,
            ID_ANY,
            choices=[e.value for e in ForceDirectedMethod]
        )
        layoutMethodChoice.SetSelection(layoutMethodChoice.FindString(p.layoutMethod.value))
        layoutMethodChoice.SetToolTip('If ‘auto’, we use ‘force’ if len(G) < 500 use ‘energy’.')
        self.Bind(EVT_CHOICE, self._onLayoutMethodChanged, layoutMethodChoice)

    def _onIterationsChanged(self, event: CommandEvent):

        newValue: int = event.GetInt()
        self._preferences.iterations = newValue

    def _onScaleFactorChange(self, event: CommandEvent):

        newValue: int = event.GetInt()
        self._preferences.frameSizeScaleFactor = newValue

    def _onNodeDistanceChange(self, event: SpinDoubleEvent):

        newValue: float = event.GetValue()
        self._preferences.optimalNodeDistance = newValue

    def _onLayoutMethodChanged(self, event: CommandEvent):

        choiceStr: str = event.GetString()
        layoutMethod: ForceDirectedMethod = ForceDirectedMethod(choiceStr)

        self._preferences.layoutMethod = layoutMethod

