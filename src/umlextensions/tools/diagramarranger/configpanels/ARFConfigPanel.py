
from logging import Logger
from logging import getLogger

from wx import CommandEvent
from wx import SpinDoubleEvent
from wx import Window

from wx.lib.sized_controls import SizedPanel

from codeallyadvanced.ui.widgets.PositionControl import PositionControl

from umlextensions.ExtensionsPreferences import ExtensionsPreferences
from umlextensions.ExtensionsPreferences import MAX_ARF_SPRING_STRENGTH
from umlextensions.ExtensionsPreferences import MAX_ITERATION_STEP_SIZE
from umlextensions.ExtensionsPreferences import MIN_ARF_SPRING_STRENGTH
from umlextensions.ExtensionsPreferences import MIN_ITERATION_STEP_SIZE
from umlextensions.tools.diagramarranger.configpanels.ValueControlSpec import ControlType

from umlextensions.tools.diagramarranger.configpanels.ValueControlSpec import ValueControlSpecs
from umlextensions.tools.diagramarranger.configpanels.ValueControlSpec import ValueControlSpec

from umlextensions.tools.diagramarranger.configpanels.BaseConfigPanel import BaseConfigPanel

SPRING_STRENGTH_INCREMENT:     float = 0.1
ITERATION_STEP_SIZE_INCREMENT: float = 0.1

class ARFConfigPanel(BaseConfigPanel):

    def __init__(self, parent: Window):

        super().__init__(parent)

        self.SetSizerType('vertical')

        self.logger: Logger = getLogger(__name__)

        self._layoutControls(parent=self, p=self._preferences)

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
                    valueLabel='Maximum Iterations',
                    spinCallback=self._onArfMaxIterationsChanged,
                    textCallback=self._onArfMaxIterationsChanged,
                    initialValue=p.arfMaxIterations,
                    controlType=ControlType.SPIN_CTRL,
                    toolTip='Number of iterations to execute. If this value is 0, it runs until convergence.'
                ),
                ValueControlSpec(
                    valueLabel='Frame Scale Factor',
                    spinCallback=self._onArfFrameScaleFactorChanged,
                    textCallback=self._onArfFrameScaleFactorChanged,
                    initialValue=p.arfFrameScaleFactor,
                    toolTip='Factor that adjusts the layout to the UML Frame size.'
                ),
                ValueControlSpec(
                    valueLabel='Spring Strength',
                    spinCallback=self._onArfSpringStrengthChanged,
                    initialValue=p.arfSpringStrength,
                    minValue=MIN_ARF_SPRING_STRENGTH,
                    maxValue=MAX_ARF_SPRING_STRENGTH,
                    spinnerIncrement=SPRING_STRENGTH_INCREMENT,
                    controlType=ControlType.SPIN_CTRL_DOUBLE,
                    toolTip='Strength of springs between the connected shapes. The larger the value the more separation between unconnected sub clusters.'
                ),
                ValueControlSpec(
                    valueLabel='Iteration Step Size',
                    spinCallback=self._onIterationStepSizeChanged,
                    initialValue=p.iterationStepSize,
                    minValue=MIN_ITERATION_STEP_SIZE,
                    maxValue=MAX_ITERATION_STEP_SIZE,
                    spinnerIncrement=ITERATION_STEP_SIZE_INCREMENT,
                    controlType=ControlType.SPIN_CTRL_DOUBLE,
                    floatDigits=3,
                    toolTip='Determines how much the shapes are allowed to move in a single iteration'
                ),
            ]
        )
        self._layoutFormControls(valueControlSpecs=valueControlSpecs, formPanel=innerForm)

    def _onArfMaxIterationsChanged(self, event: CommandEvent):
        newValue: int = event.GetInt()
        self._preferences.arfMaxIterations = newValue

    def _onArfFrameScaleFactorChanged(self, event: CommandEvent):
        newValue: int = event.GetInt()
        self._preferences.arfFrameScaleFactor = newValue

    def _onArfSpringStrengthChanged(self, event: SpinDoubleEvent):
        newValue: float = event.GetValue()
        self._preferences.arfSpringStrength = newValue

    def _onIterationStepSizeChanged(self, event: SpinDoubleEvent):
        newValue: float = event.GetValue()
        self._preferences.iterationStepSize = newValue
