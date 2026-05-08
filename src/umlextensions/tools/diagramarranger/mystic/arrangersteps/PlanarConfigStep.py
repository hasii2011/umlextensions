
from logging import Logger
from logging import getLogger

from wx.lib.sized_controls import SizedPanel

from umlextensions.tools.diagramarranger.ArrangerType import ArrangerType
from umlextensions.tools.diagramarranger.configpanels.PlanarConfigPanel import PlanarConfigPanel
from umlextensions.tools.diagramarranger.mystic.arrangersteps.BaseConfigStep import BaseConfigStep


class PlanarConfigStep(BaseConfigStep):

    TITLE:           str = 'Configure the Planar layout algorithm'

    def __init__(self, parent: SizedPanel, configuresArranger: ArrangerType):

        self.logger: Logger = getLogger(__name__)

        super().__init__(parent=parent, configuresArranger=configuresArranger)

        self._planarConfigPanel: PlanarConfigPanel = PlanarConfigPanel(parent=self)

    def _createPageTitle(self):
        """
        """
        self._createLabel(label=PlanarConfigStep.TITLE)
