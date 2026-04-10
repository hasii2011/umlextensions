
from logging import Logger
from logging import getLogger

from wx import BK_DEFAULT
from wx import ID_ANY
from wx import OK
from wx import ID_OK
from wx import CANCEL
from wx import EVT_BUTTON
from wx import EVT_CLOSE
from wx import ID_CANCEL
from wx import RESIZE_BORDER
from wx import DEFAULT_DIALOG_STYLE

from wx import Size
from wx import Notebook
from wx import CommandEvent
from wx import StdDialogButtonSizer

from wx.lib.sized_controls import SizedPanel
from wx.lib.sized_controls import SizedDialog

from umlextensions.tools.diagramarranger.configpanels.ForceAtlas2ConfigPanel import ForceAtlas2ConfigPanel
from umlextensions.tools.diagramarranger.configpanels.ARFConfigPanel import ARFConfigPanel
from umlextensions.tools.diagramarranger.configpanels.PlanarConfigPanel import PlanarConfigPanel
from umlextensions.tools.diagramarranger.configpanels.SpringConfigPanel import SpringConfigPanel


class DlgUmlDiagramArrangerPreferences(SizedDialog):

    def __init__(self, parent):

        style:   int  = DEFAULT_DIALOG_STYLE | RESIZE_BORDER
        dlgSize: Size = Size(width=490, height=400)
        #
        super().__init__(parent, title='Diagram Arranger Preferences', size=dlgSize, style=style)

        self.logger: Logger     = getLogger(__name__)
        sizedPanel:  SizedPanel = self.GetContentsPane()
        sizedPanel.SetSizerType('vertical')
        sizedPanel.SetSizerProps(proportion=1, expand=True)

        self._layoutDialog(sizedPanel=sizedPanel)
        self._layoutStandardOkCancelButtonSizer()

    def _layoutDialog(self, sizedPanel: SizedPanel):
        """

        Args:
            sizedPanel:  The parent panel

        """
        noteBook: Notebook = Notebook(sizedPanel, ID_ANY, style=BK_DEFAULT)
        noteBook.SetSizerProps(expand=True, proportion=1)

        springLayoutConfigurationPanel = SpringConfigPanel(parent=noteBook)
        arfConfigurationPanel          = ARFConfigPanel(parent=noteBook)
        planarConfigurationPanel       = PlanarConfigPanel(parent=noteBook)
        forceAtlasConfigPanel          = ForceAtlas2ConfigPanel(parent=noteBook)

        noteBook.AddPage(springLayoutConfigurationPanel, 'Spring Layout')
        noteBook.AddPage(arfConfigurationPanel, 'ARF Layout')
        noteBook.AddPage(planarConfigurationPanel, 'Planar Layout')
        noteBook.AddPage(forceAtlasConfigPanel, 'ForceAtlas2 Layout', select=True)

    def _layoutStandardOkCancelButtonSizer(self):
        """
        Call this last when creating controls; Will take care of
        adding callbacks for the Ok and Cancel buttons
        """
        buttSizer: StdDialogButtonSizer = self.CreateStdDialogButtonSizer(OK | CANCEL)

        self.SetButtonSizer(buttSizer)
        self.Bind(EVT_BUTTON, self._onOk,    id=ID_OK)
        self.Bind(EVT_BUTTON, self._onClose, id=ID_CANCEL)
        self.Bind(EVT_CLOSE,  self._onClose)

    # noinspection PyUnusedLocal
    def _onOk(self, event: CommandEvent):
        """
        """
        self.EndModal(OK)

    # noinspection PyUnusedLocal
    def _onClose(self, event: CommandEvent):
        """
        """
        self.EndModal(CANCEL)

    def _resizeDialog(self):
        """
        A little trick to make sure that you can't resize the dialog to
        less screen space than the controls need
        """
        self.Fit()
        self.SetMinSize(self.GetSize())
