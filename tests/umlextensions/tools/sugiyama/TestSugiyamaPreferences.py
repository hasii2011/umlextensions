
from unittest import main

from codeallybasic.DynamicConfiguration import KeyName
from codeallybasic.UnitTestBase import UnitTestBase

from umlextensions.tools.sugiyama.SugiyamaConstants import DEFAULT_HORIZONTAL_SPACING
from umlextensions.tools.sugiyama.SugiyamaConstants import DEFAULT_LEFT_MARGIN
from umlextensions.tools.sugiyama.SugiyamaConstants import DEFAULT_TOP_MARGIN
from umlextensions.tools.sugiyama.SugiyamaConstants import DEFAULT_VERTICAL_SPACING
from umlextensions.tools.sugiyama.SugiyamaPreferences import SECTION_SUGIYAMA_LAYOUT
from umlextensions.tools.sugiyama.SugiyamaPreferences import SugiyamaPreferences
from umlextensions.tools.sugiyama.VirtualSugiyamaNode import VirtualSugiyamaNode


class TestSugiyamaPreferences(UnitTestBase):
    """
    Unit tests for SugiyamaPreferences dedicated configuration storage.
    """

    def setUp(self):
        super().setUp()
        self._preferences: SugiyamaPreferences = SugiyamaPreferences()
        self._origLeftMargin:        int  = self._preferences.leftMargin
        self._origTopMargin:         int  = self._preferences.topMargin
        self._origHorizontalSpacing: int  = self._preferences.horizontalSpacing
        self._origVerticalSpacing:   int  = self._preferences.verticalSpacing
        self._origStepByStep:        bool = self._preferences.sugiyamaStepByStep

    def tearDown(self):
        self._preferences.leftMargin        = self._origLeftMargin
        self._preferences.topMargin         = self._origTopMargin
        self._preferences.horizontalSpacing = self._origHorizontalSpacing
        self._preferences.verticalSpacing   = self._origVerticalSpacing
        self._preferences.sugiyamaStepByStep = self._origStepByStep
        super().tearDown()

    def testDefaults(self):
        """
        Verify default spacing, margin, and step-by-step values in schema match constants.
        """
        self.assertEqual(int(SECTION_SUGIYAMA_LAYOUT[KeyName('leftMargin')].defaultValue), DEFAULT_LEFT_MARGIN)
        self.assertEqual(int(SECTION_SUGIYAMA_LAYOUT[KeyName('topMargin')].defaultValue), DEFAULT_TOP_MARGIN)
        self.assertEqual(int(SECTION_SUGIYAMA_LAYOUT[KeyName('horizontalSpacing')].defaultValue), DEFAULT_HORIZONTAL_SPACING)
        self.assertEqual(int(SECTION_SUGIYAMA_LAYOUT[KeyName('verticalSpacing')].defaultValue), DEFAULT_VERTICAL_SPACING)
        self.assertEqual(SECTION_SUGIYAMA_LAYOUT[KeyName('sugiyamaStepByStep')].defaultValue, 'False')

    def testSettersAndGetters(self):
        """
        Verify runtime mutation and type roundtrip for all preferences.
        """
        testLeftMargin:        int = 42
        testTopMargin:         int = 55
        testHorizontalSpacing: int = 75
        testVerticalSpacing:   int = 120

        self._preferences.leftMargin        = testLeftMargin
        self._preferences.topMargin         = testTopMargin
        self._preferences.horizontalSpacing = testHorizontalSpacing
        self._preferences.verticalSpacing   = testVerticalSpacing
        self._preferences.sugiyamaStepByStep = True

        self.assertEqual(self._preferences.leftMargin, testLeftMargin)
        self.assertEqual(self._preferences.topMargin, testTopMargin)
        self.assertEqual(self._preferences.horizontalSpacing, testHorizontalSpacing)
        self.assertEqual(self._preferences.verticalSpacing, testVerticalSpacing)
        self.assertTrue(self._preferences.sugiyamaStepByStep)

    def testNodeHorizontalSpacingResolution(self):
        """
        Verify node defaults to preferences when not explicitly provided,
        and honors explicit constructor override when provided.
        """
        expectedPrefsHorizontalSpacing: int = self._preferences.horizontalSpacing
        defaultNode: VirtualSugiyamaNode = VirtualSugiyamaNode()
        self.assertEqual(defaultNode._horizontalSpacing, expectedPrefsHorizontalSpacing)

        self._preferences.horizontalSpacing = 88
        customPrefsNode: VirtualSugiyamaNode = VirtualSugiyamaNode()
        self.assertEqual(customPrefsNode._horizontalSpacing, 88)

        explicitNode: VirtualSugiyamaNode = VirtualSugiyamaNode(horizontalSpacing=120)
        self.assertEqual(explicitNode._horizontalSpacing, 120)

        explicitDefaultNode: VirtualSugiyamaNode = VirtualSugiyamaNode(horizontalSpacing=DEFAULT_HORIZONTAL_SPACING)
        self.assertEqual(explicitDefaultNode._horizontalSpacing, DEFAULT_HORIZONTAL_SPACING)


if __name__ == '__main__':
    main()
