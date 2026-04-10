
from wx import CommandEvent
from wx import SpinDoubleEvent
from wx import Window

from wx.lib.sized_controls import SizedPanel

from codeallyadvanced.ui.widgets.PositionControl import PositionControl

from umlextensions.ExtensionsPreferences import ExtensionsPreferences
from umlextensions.tools.diagramarranger.configpanels.BaseConfigPanel import BaseConfigPanel
from umlextensions.tools.diagramarranger.configpanels.ValueControlSpec import ControlType
from umlextensions.tools.diagramarranger.configpanels.ValueControlSpec import ValueControlSpecs
from umlextensions.tools.diagramarranger.configpanels.ValueControlSpec import ValueControlSpec

JITTER_TOLERANCE_INCREMENT: float = 0.1
JITTER_TOLERANCE_MIN_VALUE: float = 0.1
JITTER_TOLERANCE_MAX_VALUE: float = 10.0

SCALING_RATIO_INCREMENT: float = 0.1
SCALING_RATIO_MIN_VALUE: float = 0.1
SCALING_RATIO_MAX_VALUE: float = 10.0

class ForceAtlas2ConfigPanel(BaseConfigPanel):

    def __init__(self, parent: Window):

        super().__init__(parent)

        self.SetSizerType('vertical')

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
                    spinCallback=self._onMaxIterationsChanged,
                    textCallback=self._onMaxIterationsChanged,
                    initialValue=p.atlasMaxIterations,
                    controlType=ControlType.SPIN_CTRL,
                    toolTip='Number of iterations to execute.'
                ),
                ValueControlSpec(
                    valueLabel='Jitter Tolerance',
                    spinCallback=self._onJitterToleranceChanged,
                    initialValue=p.jitterTolerance,
                    toolTip='Adjusts the oscillation of shapes',
                    controlType=ControlType.SPIN_CTRL_DOUBLE,
                    spinnerIncrement=JITTER_TOLERANCE_INCREMENT,
                    minValue=JITTER_TOLERANCE_MIN_VALUE,
                    maxValue=JITTER_TOLERANCE_MAX_VALUE
                ),
                ValueControlSpec(
                    valueLabel='Scaling Ratio',
                    spinCallback=self._onScalingRatioChanged,
                    initialValue=p.scalingRatio,
                    toolTip='The scaling of attraction and repulsion forces.',
                    controlType=ControlType.SPIN_CTRL_DOUBLE,
                    spinnerIncrement = SCALING_RATIO_INCREMENT,
                    minValue = SCALING_RATIO_MIN_VALUE,
                    maxValue = SCALING_RATIO_MAX_VALUE
                ),
                ValueControlSpec(
                    valueLabel='Gravity',
                    spinCallback=self._onGravityChanged,
                    initialValue=p.gravity,
                    controlType=ControlType.SPIN_CTRL_DOUBLE,
                    toolTip='The attraction force on shapes to the center.'
                ),
                ValueControlSpec(
                    valueLabel='Distributed Action',
                    checkBoxCallback=self._onDistributedActionChanged,
                    initialValue=p.distributedAction,
                    controlType=ControlType.CHECK_BOX,
                    toolTip='If True, evenly distribute the attraction force among all the shapes.'
                ),
                ValueControlSpec(
                    valueLabel='Strong Gravity',
                    checkBoxCallback=self._onStrongGravityChanged,
                    initialValue=p.strongGravity,
                    controlType=ControlType.CHECK_BOX,
                    toolTip='If True, apply a strong gravitational pull towards the center.'
                ),
                ValueControlSpec(
                    valueLabel='Logarithmic Attraction',
                    checkBoxCallback=self._onLogarithmicAttractionChanged,
                    initialValue=p.logarithmicAttraction,
                    controlType=ControlType.CHECK_BOX,
                    toolTip='If True, Use logarithmic attraction instead of linear attraction.'
                ),
                ValueControlSpec(
                    valueLabel='Prevent Shape Crowding',
                    checkBoxCallback=self._onPreventShapeCrowdingChanged,
                    initialValue=p.preventShapeCrowding,
                    controlType=ControlType.CHECK_BOX,
                    toolTip='If True, shapes size is used to prevent crowding.'
                ),
            ]
        )
        self._layoutFormControls(valueControlSpecs=valueControlSpecs, formPanel=innerForm)

    def _onMaxIterationsChanged(self, event: CommandEvent):

        newValue: int = event.GetInt()
        self._preferences.atlasMaxIterations = newValue

    def _onJitterToleranceChanged(self, event: SpinDoubleEvent):
        newValue: float = event.GetValue()
        self._preferences.jitterTolerance = newValue

    def _onScalingRatioChanged(self, event: SpinDoubleEvent):
        newValue: float = event.GetValue()
        self._preferences.scalingRatio = newValue

    def _onGravityChanged(self, event: SpinDoubleEvent):
        newValue: float = event.GetValue()
        self._preferences.gravity = newValue

    def _onDistributedActionChanged(self, event: CommandEvent):
        newValue: bool = event.IsChecked()
        self._preferences.distributedAction = newValue

    def _onStrongGravityChanged(self, event: CommandEvent):
        newValue: bool = event.IsChecked()
        self._preferences.strongGravity = newValue

    def _onLogarithmicAttractionChanged(self, event: CommandEvent):
        newValue: bool = event.IsChecked()
        self._preferences.logarithmicAttraction = newValue

    def _onPreventShapeCrowdingChanged(self, event: CommandEvent):
        newValue: bool = event.IsChecked()
        self._preferences.preventShapeCrowding = newValue
