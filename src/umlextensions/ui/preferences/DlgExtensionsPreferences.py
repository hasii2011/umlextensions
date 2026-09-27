
from logging import Logger
from logging import getLogger

from wx import CANCEL
from wx import DEFAULT_DIALOG_STYLE
from wx import EVT_BUTTON
from wx import EVT_CLOSE
from wx import ID_ANY
from wx import ID_OK
from wx import NB_TOP
from wx import OK
from wx import RESIZE_BORDER

from wx import CommandEvent
from wx import Notebook
from wx import Size
from wx import Window

from wx.lib.sized_controls import SizedDialog
from wx.lib.sized_controls import SizedPanel

from umlextensions.ui.preferences.ArrangerSectionPanel import ArrangerSectionPanel
from umlextensions.ui.preferences.ExtensionsSectionPanel import ExtensionsSectionPanel
from umlextensions.ui.preferences.FeaturesSectionPanel import FeaturesSectionPanel
from umlextensions.ui.preferences.ShapeLayoutSectionPanel import ShapeLayoutSectionPanel
from umlextensions.ui.preferences.TooltipSectionPanel import TooltipSectionPanel


class DlgExtensionsPreferences(SizedDialog):
    """
    Standalone preferences dialog for the umlextensions demo application.

    Displays all ExtensionsPreferences sections as notebook tabs and
    saves changes immediately as each control is modified (no Apply button
    needed — mirrors how macOS preferences work).

    Usage:
    ```python
    with DlgExtensionsPreferences(parent=self._frame) as dlg:
        dlg.ShowModal()
    ```
    """

    def __init__(self, parent: Window):
        """
        Args:
            parent:  The parent wx.Window (typically an application frame)
        """
        self.logger: Logger = getLogger(__name__)

        style:   int  = DEFAULT_DIALOG_STYLE | RESIZE_BORDER
        dlgSize: Size = Size(width=560, height=680)

        super().__init__(parent, ID_ANY, 'Extensions Preferences', size=dlgSize, style=style)

        sizedPanel: SizedPanel = self.GetContentsPane()
        sizedPanel.SetSizerProps(expand=True, proportion=1)

        self._createTheControls(sizedPanel=sizedPanel)

        self.SetButtonSizer(self.CreateStdDialogButtonSizer(OK))

        self.Bind(EVT_BUTTON, self._onOk, id=ID_OK)
        self.Bind(EVT_CLOSE,  self._onClose)

    def _createTheControls(self, sizedPanel: SizedPanel):
        """
        Build the top-level Notebook with one tab per INI section group.

        Args:
            sizedPanel:  The dialog's contents pane
        """
        book: Notebook = Notebook(sizedPanel, style=NB_TOP)
        book.SetSizerProps(expand=True, proportion=1)

        extensionsPanel:  ExtensionsSectionPanel  = ExtensionsSectionPanel(book)
        featuresPanel:    FeaturesSectionPanel    = FeaturesSectionPanel(book)
        shapeLayoutPanel: ShapeLayoutSectionPanel = ShapeLayoutSectionPanel(book)
        arrangerPanel:    ArrangerSectionPanel    = ArrangerSectionPanel(book)
        tooltipPanel:     TooltipSectionPanel     = TooltipSectionPanel(book)

        book.AddPage(extensionsPanel,  text=extensionsPanel.name,  select=True)
        book.AddPage(featuresPanel,    text=featuresPanel.name,    select=False)
        book.AddPage(shapeLayoutPanel, text=shapeLayoutPanel.name, select=False)
        book.AddPage(arrangerPanel,    text=arrangerPanel.name,    select=False)
        book.AddPage(tooltipPanel,     text=tooltipPanel.name,     select=False)

    # noinspection PyUnusedLocal
    def _onOk(self, event: CommandEvent):
        self.EndModal(OK)
        event.Skip(skip=True)

    def _onClose(self, event: CommandEvent):
        self.EndModal(CANCEL)
        event.Skip(skip=True)
