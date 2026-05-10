
from logging import Logger
from logging import getLogger

from umlshapes.ShapeTypes import UmlShapes

from umlextensions.IExtensionsFacade import IExtensionsFacade

from umlextensions.extensiontypes.ExtensionDataTypes import Author
from umlextensions.extensiontypes.ExtensionDataTypes import ExtensionName
from umlextensions.extensiontypes.ExtensionDataTypes import Version

from umlextensions.tools.BaseToolExtension import BaseToolExtension
from umlextensions.tools.diagramarranger.ArrangerType import ArrangerType

from umlextensions.tools.diagramarranger.LayoutAlgorithms import LayoutAlgorithms
from umlextensions.tools.diagramarranger.mystic.MysticAdapter import MysticAdapter


class ToolDiagramArranger(BaseToolExtension):

    def __init__(self, extensionsFacade: IExtensionsFacade):

        super().__init__(extensionsFacade=extensionsFacade)
        self.logger: Logger = getLogger(__name__)

        self._name    = ExtensionName('Diagram Arranger')
        self._author  = Author('Humberto A. Sanchez II')
        self._version = Version('1.0')

        self._displayBusyCursor = False

    def setOptions(self) -> bool:
        return True

    def doAction(self):

        mysticAdapter: MysticAdapter = MysticAdapter(
            parent=self._frameInformation.umlFrame,
            completeCallback=self._completeCallback,
            cancelCallback=self._cancelCallback,
            layoutCallback=self._layoutCallback,
            undoCallback=self._undoCallback
        )
        mysticAdapter.run()

    def _completeCallback(self):
        pass

    def _cancelCallback(self):
        """
        Undo the last layout
        """
        pass

    def _layoutCallback(self, arrangerType: ArrangerType):
        """
        Run the appropriate layout algorithm
        Args:
            arrangerType:

        """

        selectedUmlShapes: UmlShapes = self._frameInformation.selectedUmlShapes

        layouts: LayoutAlgorithms = LayoutAlgorithms()
        if arrangerType == ArrangerType.SPRING:
            layouts.applySpringLayout(umlFrame=self._frameInformation.umlFrame, umlShapes=selectedUmlShapes)
        elif arrangerType == ArrangerType.ARF:
            layouts.applyArfLayout(umlFrame=self._frameInformation.umlFrame, umlShapes=selectedUmlShapes)
        elif arrangerType == ArrangerType.PLANAR:
            layouts.applyPlanarLayout(umlFrame=self._frameInformation.umlFrame, umlShapes=selectedUmlShapes)
        elif arrangerType == ArrangerType.FORCE_ATLAS2:
            layouts.applyForceAtlas2Layout(umlFrame=self._frameInformation.umlFrame, umlShapes=selectedUmlShapes)
        else:
            assert False, 'Developer error;  Unknown arranger type'

    def _undoCallback(self):
        pass
