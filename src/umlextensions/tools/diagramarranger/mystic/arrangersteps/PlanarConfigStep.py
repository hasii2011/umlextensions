
from logging import Logger
from logging import getLogger

from wx.lib.sized_controls import SizedPanel

from umlextensions.tools.diagramarranger.ArrangerType import ArrangerType
from umlextensions.tools.diagramarranger.configpanels.PlanarConfigPanel import PlanarConfigPanel
from umlextensions.tools.diagramarranger.mystic.arrangersteps.BaseConfigStep import BaseConfigStep
from umlextensions.tools.diagramarranger.mystic.arrangersteps.BaseConfigStep import LayoutCallback
from umlextensions.tools.diagramarranger.mystic.arrangersteps.BaseConfigStep import UndoCallback


class PlanarConfigStep(BaseConfigStep):

    TITLE:           str = 'Configure the Planar layout algorithm'

    def __init__(self, parent: SizedPanel, configuresArranger: ArrangerType, layoutCallback: LayoutCallback, undoCallback: UndoCallback):
        """

        Args:
            parent:
            configuresArranger:     They type of arranger configuration we configure
            layoutCallback:         Method to call to re-arrange UML Diagram
            undoCallback:           Method to call to undo last arrangement
        """

        self.logger: Logger = getLogger(__name__)

        super().__init__(parent=parent, configuresArranger=configuresArranger, layoutCallback=layoutCallback, undoCallback=undoCallback)

    def _layoutPageTitle(self):
        """
        """
        self._createLabel(label=PlanarConfigStep.TITLE)

    def _layoutConfigPanel(self):
        self._planarConfigPanel: PlanarConfigPanel = PlanarConfigPanel(parent=self)
