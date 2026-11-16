
from unittest import main

from wx import Frame
from wx import Window
from wx import CommandEvent
from wx import EVT_SPINCTRL
from wx import EVT_CHECKBOX

from codeallyadvanced.ui.UnitTestBaseW import UnitTestBaseW

from umlextensions.tools.sugiyama.SugiyamaPreferences import SugiyamaPreferences
from umlextensions.ui.preferences.SugiyamaPanel import SugiyamaPanel
from umlextensions.ui.preferences.SugiyamaPanel import TOOLTIP_LEFT_MARGIN
from umlextensions.ui.preferences.SugiyamaPanel import TOOLTIP_TOP_MARGIN
from umlextensions.ui.preferences.SugiyamaPanel import TOOLTIP_HORIZONTAL_SPACING
from umlextensions.ui.preferences.SugiyamaPanel import TOOLTIP_VERTICAL_SPACING
from umlextensions.ui.preferences.SugiyamaPanel import TOOLTIP_STEP_BY_STEP


class TestSugiyamaPanel(UnitTestBaseW):
    """
    Unit tests for the Sugiyama preferences panel UI.
    """

    def setUp(self):
        super().setUp()
        self._preferences: SugiyamaPreferences = SugiyamaPreferences()
        self._origLeftMargin:        int  = self._preferences.leftMargin
        self._origTopMargin:         int  = self._preferences.topMargin
        self._origHorizontalSpacing: int  = self._preferences.horizontalSpacing
        self._origVerticalSpacing:   int  = self._preferences.verticalSpacing
        self._origStepByStep:        bool = self._preferences.sugiyamaStepByStep

        self._parentFrame: Frame = Frame(None)
        self._panel: SugiyamaPanel = SugiyamaPanel(parent=self._parentFrame)

    def tearDown(self):
        self._parentFrame.Destroy()
        self._preferences.leftMargin        = self._origLeftMargin
        self._preferences.topMargin         = self._origTopMargin
        self._preferences.horizontalSpacing = self._origHorizontalSpacing
        self._preferences.verticalSpacing   = self._origVerticalSpacing
        self._preferences.sugiyamaStepByStep = self._origStepByStep
        super().tearDown()

    def testPanelInitialization(self):
        """
        Verify controls are populated with current preference values upon construction.
        """
        self.assertEqual(self._panel.name, 'Sugiyama')
        self.assertEqual(self._panel._leftMarginCtrl.GetValue(),         self._preferences.leftMargin)
        self.assertEqual(self._panel._topMarginCtrl.GetValue(),          self._preferences.topMargin)
        self.assertEqual(self._panel._horizontalSpacingCtrl.GetValue(), self._preferences.horizontalSpacing)
        self.assertEqual(self._panel._verticalSpacingCtrl.GetValue(),   self._preferences.verticalSpacing)
        self.assertEqual(self._panel._stepByStepCtrl.GetValue(),         self._preferences.sugiyamaStepByStep)

    def testControlModificationsUpdatePreferences(self):
        """
        Verify that changing UI controls updates backing SugiyamaPreferences.
        """
        self._panel._leftMarginCtrl.SetValue(35)
        self._panel._onLeftMarginChanged(CommandEvent(EVT_SPINCTRL.typeId))
        self.assertEqual(self._preferences.leftMargin, 35)

        self._panel._topMarginCtrl.SetValue(45)
        self._panel._onTopMarginChanged(CommandEvent(EVT_SPINCTRL.typeId))
        self.assertEqual(self._preferences.topMargin, 45)

        self._panel._horizontalSpacingCtrl.SetValue(65)
        self._panel._onHorizontalSpacingChanged(CommandEvent(EVT_SPINCTRL.typeId))
        self.assertEqual(self._preferences.horizontalSpacing, 65)

        self._panel._verticalSpacingCtrl.SetValue(95)
        self._panel._onVerticalSpacingChanged(CommandEvent(EVT_SPINCTRL.typeId))
        self.assertEqual(self._preferences.verticalSpacing, 95)

        self._panel._stepByStepCtrl.SetValue(True)
        self._panel._onStepByStepChanged(CommandEvent(EVT_CHECKBOX.typeId))
        self.assertTrue(self._preferences.sugiyamaStepByStep)

    def testTooltipsConfigured(self):
        """
        Verify tooltips are set on controls.
        """
        self.assertEqual(self._panel._leftMarginCtrl.GetToolTipText(),         TOOLTIP_LEFT_MARGIN)
        self.assertEqual(self._panel._topMarginCtrl.GetToolTipText(),          TOOLTIP_TOP_MARGIN)
        self.assertEqual(self._panel._horizontalSpacingCtrl.GetToolTipText(), TOOLTIP_HORIZONTAL_SPACING)
        self.assertEqual(self._panel._verticalSpacingCtrl.GetToolTipText(),   TOOLTIP_VERTICAL_SPACING)
        self.assertEqual(self._panel._stepByStepCtrl.GetToolTipText(),         TOOLTIP_STEP_BY_STEP)


if __name__ == '__main__':
    main()
