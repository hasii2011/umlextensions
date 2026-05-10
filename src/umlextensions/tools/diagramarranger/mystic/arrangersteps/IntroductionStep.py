
from wx import ID_ANY
from wx import StaticLine
from wx import StaticText

from wx.lib.sized_controls import SizedPanel

from codeallyadvanced.ui.mystic.MysticStepBase import MysticStepBase


class IntroductionStep(MysticStepBase):

    TITLE_FONT_SIZE: int = 18

    TITLE: str = 'Introduction'

    INTRODUCTION_TEXT: str = """
    This wizard will guide you through various steps to run various UML Shape
    layout algorithms.
    
    Each algorithm has a set of various configuration parameters.  Each algorithm
    will have an `undo` option in order to run the layout again with
    different parameters

    """

    def __init__(self, parent: SizedPanel):

        super().__init__(parent=parent)

        self.SetSizerType('vertical')

        self._createPageTitle()
        self._createIntroductionText()

    def _createPageTitle(self):
        """
        """
        self._createLabel(label=IntroductionStep.TITLE, fontSize=IntroductionStep.TITLE_FONT_SIZE)
        StaticLine(parent=self, id=ID_ANY)

    def _createIntroductionText(self):

        StaticText(parent=self, id=ID_ANY, label=IntroductionStep.INTRODUCTION_TEXT)
