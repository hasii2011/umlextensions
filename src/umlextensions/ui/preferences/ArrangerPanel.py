
from typing import cast

from logging import Logger
from logging import getLogger

from wx import Choice
from wx import CommandEvent
from wx import EVT_CHOICE
from wx import ID_ANY
from wx import NB_TOP
from wx import Notebook
from wx import Size
from wx import StaticText
from wx import Window

from wx.lib.sized_controls import SizedStaticBox

from umlextensions.tools.diagramarranger.ArrangerType import ArrangerType
from umlextensions.tools.diagramarranger.configpanels.ARFConfigPanel import ARFConfigPanel
from umlextensions.tools.diagramarranger.configpanels.ForceAtlas2ConfigPanel import ForceAtlas2ConfigPanel
from umlextensions.tools.diagramarranger.configpanels.PlanarConfigPanel import PlanarConfigPanel
from umlextensions.tools.diagramarranger.configpanels.SpringConfigPanel import SpringConfigPanel
from umlextensions.ExtensionsPreferences import ExtensionsPreferences
from umlextensions.ui.preferences.BasePreferencesPanel import BasePreferencesPanel


class ArrangerPanel(BasePreferencesPanel):
    """
    Preferences panel for the Arranger-related INI sections:

        Arranger Common   - layoutCenter, defaultArranger
        Spring Layout     - delegates to SpringConfigPanel
        ARF Layout        - delegates to ARFConfigPanel
        Planar Layout     - delegates to PlanarConfigPanel
        Force Atlas2      - delegates to ForceAtlas2ConfigPanel

    Uses a nested Notebook so each layout subsection gets its own tab,
    keeping the top-level preferences dialog clean (one 'Arranger' tab).
    """

    PANEL_NAME: str = 'Arranger'

    def __init__(self, parent: Window):

        super().__init__(parent)

        self.logger: Logger = getLogger(__name__)

        self.SetSizerType('vertical')

        self._defaultArrangerChoice: Choice = cast(Choice, None)    # noqa

        self._layoutControls()
        self._setControlValues()

    @property
    def name(self) -> str:
        return ArrangerPanel.PANEL_NAME

    def _layoutControls(self):
        """
        Builds and lays out the controls for the Arranger preferences.
        """
        self._layoutCommonSettings()
        self._layoutAlgorithmNotebook()

    def _layoutCommonSettings(self):
        """
        Lays out the common arranger settings group.
        """
        commonBox: SizedStaticBox = SizedStaticBox(self, ID_ANY, 'Common Settings')
        commonBox.SetSizerType('form')
        commonBox.SetMinSize(Size(-1, 60))
        commonBox.SetSizerProps(expand=True)

        arrangerLabel: StaticText = StaticText(commonBox, ID_ANY, 'Default Arranger')
        arrangerLabel.SetSizerProps(valign='center')
        self._defaultArrangerChoice = Choice(
            commonBox,
            ID_ANY,
            choices=[e.value for e in ArrangerType]
        )
        self._defaultArrangerChoice.SetSizerProps(expand=True, valign='center')
        self._defaultArrangerChoice.SetToolTip('The arranger algorithm used by default when none is specified')
        self.Bind(EVT_CHOICE, self._onDefaultArrangerChanged, self._defaultArrangerChoice)

    def _layoutAlgorithmNotebook(self):
        """
        Lays out the nested notebook for individual algorithm configurations.
        """
        subBook: Notebook = Notebook(self, style=NB_TOP)
        subBook.SetSizerProps(expand=True, proportion=1)

        springPanel:     SpringConfigPanel     = SpringConfigPanel(subBook)
        arfPanel:        ARFConfigPanel        = ARFConfigPanel(subBook)
        planarPanel:     PlanarConfigPanel     = PlanarConfigPanel(subBook)
        forceAtlas2Panel: ForceAtlas2ConfigPanel = ForceAtlas2ConfigPanel(subBook)

        subBook.AddPage(springPanel,      text='Spring',      select=True)
        subBook.AddPage(arfPanel,         text='ARF',         select=False)
        subBook.AddPage(planarPanel,      text='Planar',      select=False)
        subBook.AddPage(forceAtlas2Panel, text='ForceAtlas2', select=False)

    def _setControlValues(self):

        p: ExtensionsPreferences = self._preferences

        defaultArranger: ArrangerType = p.defaultArranger
        idx: int = self._defaultArrangerChoice.FindString(defaultArranger.value)
        if idx >= 0:
            self._defaultArrangerChoice.SetSelection(idx)

    def _onDefaultArrangerChanged(self, event: CommandEvent):
        choiceStr: str = event.GetString()
        self._preferences.defaultArranger = ArrangerType(choiceStr)

