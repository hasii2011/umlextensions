
from logging import Logger
from logging import getLogger

from wx.lib.sized_controls import SizedFrame
from wx.lib.sized_controls import SizedPanel

from wx import DEFAULT_FRAME_STYLE
from wx import FRAME_FLOAT_ON_PARENT

FRAME_WIDTH:  int = 1024
FRAME_HEIGHT: int = 720


class ExtensionFrame(SizedFrame):
    def __init__(self):
        self.logger: Logger = getLogger(__name__)
        super().__init__(parent=None, title='Demo UML Extensions', size=(FRAME_WIDTH, FRAME_HEIGHT), style=DEFAULT_FRAME_STYLE | FRAME_FLOAT_ON_PARENT)

        sizedPanel: SizedPanel = self.GetContentsPane()
        sizedPanel.SetSizerProps(expand=True, proportion=1)
