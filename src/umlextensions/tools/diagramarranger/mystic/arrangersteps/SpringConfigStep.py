
from logging import Logger
from logging import getLogger

from wx.lib.sized_controls import SizedPanel

from umlextensions.tools.diagramarranger.ArrangerType import ArrangerType
from umlextensions.tools.diagramarranger.configpanels.SpringConfigPanel import SpringConfigPanel
from umlextensions.tools.diagramarranger.mystic.arrangersteps.BaseConfigStep import BaseConfigStep


class SpringConfigStep(BaseConfigStep):

    TITLE: str = 'Configure the Spring layout algorithm'

    def __init__(self, parent: SizedPanel, configuresArranger: ArrangerType):
        """

        Args:
            parent:
            configuresArranger:
        """

        self.logger: Logger = getLogger(__name__)

        super().__init__(parent=parent, configuresArranger=configuresArranger)

        self._springConfigPanel: SpringConfigPanel = SpringConfigPanel(parent=self)

    def _createPageTitle(self):
        """
        """
        self._createLabel(label=SpringConfigStep.TITLE)
