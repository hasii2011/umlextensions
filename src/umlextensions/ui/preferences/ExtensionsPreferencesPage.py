
from logging import Logger
from logging import getLogger

from wx import ID_ANY
from wx import NB_TOP

from wx import Window
from wx import Notebook

from wx.lib.sized_controls import SizedPanel

from umlextensions.ui.preferences.ArrangerPanel import ArrangerPanel
from umlextensions.ui.preferences.ExtensionsPanel import ExtensionsPanel
from umlextensions.ui.preferences.FeaturesPanel import FeaturesPanel
from umlextensions.ui.preferences.ShapeLayoutPanel import ShapeLayoutPanel
from umlextensions.ui.preferences.TooltipPanel import TooltipPanel


class ExtensionsPreferencesPage(SizedPanel):
    """
    A single SizedPanel page that encapsulates all umlextensions preferences
    inside a nested Notebook with one tab per INI section group.

    Architectural Rationale:
        1. Encapsulation & Decoupling:
           Acts as a facade component for host applications (such as UML Diagrammer).
           The host application only needs to import and instantiate this single class,
           completely decoupling it from the individual section panels (Extensions,
           Features, Shape Layout, Arranger, and Tooltip).

        2. Independent Evolution:
           Any future preferences sections added, reordered, or redesigned within
           umlextensions are automatically surfaced to the host application without
           requiring code changes in UML Diagrammer.

        3. wxWidgets & macOS Container Integrity:
           In wxWidgets (particularly on macOS Cocoa), adding a wx.Notebook directly
           as a child page of another wx.Notebook without an intervening wx.Panel
           frequently causes background rendering artifacts, focus ring glitches,
           and sizer resize issues. Wrapping the nested notebook in this SizedPanel
           guarantees native macOS background rendering and proper sizer propagation.

    Usage in UML Diagrammer:
        ```python
        from umlextensions.ui.preferences.ExtensionsPreferencesPage import ExtensionsPreferencesPage

        extensionsPage: ExtensionsPreferencesPage = ExtensionsPreferencesPage(mainPreferencesBook)
        mainPreferencesBook.AddPage(extensionsPage, text=extensionsPage.name, select=False)
        ```
    """

    PAGE_NAME: str = 'Extensions'

    def __init__(self, parent: Window):

        super().__init__(parent)

        self.logger: Logger = getLogger(__name__)

        self.SetSizerType('vertical')

        self._createSubNotebook()

    @property
    def name(self) -> str:
        """
        The label text used when this page is added to a parent Notebook.
        """
        return ExtensionsPreferencesPage.PAGE_NAME

    def _createSubNotebook(self):
        """
        Build the nested Notebook and add all section panels as pages.
        """
        subBook: Notebook = Notebook(self, ID_ANY, style=NB_TOP)
        subBook.SetSizerProps(expand=True, proportion=1)

        extensionsPanel:  ExtensionsPanel  = ExtensionsPanel(subBook)
        featuresPanel:    FeaturesPanel    = FeaturesPanel(subBook)
        shapeLayoutPanel: ShapeLayoutPanel = ShapeLayoutPanel(subBook)
        arrangerPanel:    ArrangerPanel    = ArrangerPanel(subBook)
        tooltipPanel:     TooltipPanel     = TooltipPanel(subBook)

        subBook.AddPage(extensionsPanel,  text=extensionsPanel.name,  select=True)
        subBook.AddPage(featuresPanel,    text=featuresPanel.name,    select=False)
        subBook.AddPage(shapeLayoutPanel, text=shapeLayoutPanel.name, select=False)
        subBook.AddPage(arrangerPanel,    text=arrangerPanel.name,    select=False)
        subBook.AddPage(tooltipPanel,     text=tooltipPanel.name,     select=False)
