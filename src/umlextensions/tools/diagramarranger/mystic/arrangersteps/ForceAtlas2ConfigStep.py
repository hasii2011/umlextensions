
from logging import Logger
from logging import getLogger

from wx.lib.sized_controls import SizedPanel

from umlextensions.tools.diagramarranger.ArrangerType import ArrangerType
from umlextensions.tools.diagramarranger.configpanels.ForceAtlas2ConfigPanel import ForceAtlas2ConfigPanel
from umlextensions.tools.diagramarranger.mystic.arrangersteps.BaseConfigStep import BaseConfigStep


class ForceAtlas2ConfigStep(BaseConfigStep):
    TITLE: str = 'Configure the ForceAtlas2 layout algorithm'

    def __init__(self, parent: SizedPanel, configuresArranger: ArrangerType):

        self.logger: Logger = getLogger(__name__)

        super().__init__(parent=parent, configuresArranger=configuresArranger)

        self._forceAtlas2ConfigPanel: ForceAtlas2ConfigPanel = ForceAtlas2ConfigPanel(parent=self)

    def _createPageTitle(self):
        """
        """
        self._createLabel(label=ForceAtlas2ConfigStep.TITLE)
