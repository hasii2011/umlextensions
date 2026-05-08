
from logging import Logger
from logging import getLogger

from wx import EVT_CHOICE
from wx import CommandEvent

from wx import Choice

from wx.lib.sized_controls import SizedPanel

from umlextensions.ExtensionsPreferences import ExtensionsPreferences
from umlextensions.tools.diagramarranger.ArrangerType import ArrangerType

from codeallyadvanced.ui.mystic.MysticStepBase import MysticStepBase


class LayoutSelectionStep(MysticStepBase):
    TITLE: str = 'Select shape layout algorithm'

    def __init__(self, parent: SizedPanel):

        self.logger: Logger = getLogger(__name__)

        super().__init__(parent=parent)

        self._preferences: ExtensionsPreferences = ExtensionsPreferences()

        self.SetSizerType('vertical')
        self.SetSizerProps(expand=True, proportion=1)      # noqa

        self._createPageTitle()
        arrangeTypes = [s.value for s in ArrangerType]

        self._layoutAlgorithm: Choice = Choice(self, choices=arrangeTypes)
        self._layoutAlgorithm.SetSizerProps(expand=True, proportion=1)

        defaultLayoutAlgorithmIdx: int = arrangeTypes.index(self._preferences.defaultArranger.value)
        self._layoutAlgorithm.SetSelection(defaultLayoutAlgorithmIdx)

        self.Bind(EVT_CHOICE, self._onAlgorithmChanged, self._layoutAlgorithm)

    @property
    def arrangerType(self) -> ArrangerType:

        idx:         int = self._layoutAlgorithm.GetSelection()
        arrangerStr: str = self._layoutAlgorithm.GetString(idx)

        return ArrangerType(arrangerStr)

    def _onAlgorithmChanged(self, event: CommandEvent):

            algorithmStr: str = event.GetString()
            self.logger.info(f'{algorithmStr=}')

    def _createPageTitle(self):
        """
        """
        self._createLabel(label=LayoutSelectionStep.TITLE)
