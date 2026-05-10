
from codeallyadvanced.ui.mystic.MysticStepBase import MysticStepBase
from wx import ID_ANY
from wx import StaticLine
from wx.lib.sized_controls import SizedPanel


class GoodByeStep(MysticStepBase):
    TITLE_FONT_SIZE: int = 18

    TITLE: str = 'Good Bye'

    GOODBYE_TEXT: str = """
        Thanks for using this tool extensions
                -- Humberto A. Sanchez II
    """

    def __init__(self, parent: SizedPanel):

        super().__init__(parent=parent)

        self.SetSizerType('vertical')

        self._createPageTitle()

    def _createPageTitle(self):
        """
        """
        self._createLabel(label=GoodByeStep.TITLE, fontSize=GoodByeStep.TITLE_FONT_SIZE)
        StaticLine(parent=self, id=ID_ANY)
