
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

class ToolDiagramArranger(BaseToolExtension):

    def __init__(self, extensionsFacade: IExtensionsFacade):

        super().__init__(extensionsFacade=extensionsFacade)
        self.logger: Logger = getLogger(__name__)

        self._name    = ExtensionName('Diagram Arranger')
        self._author  = Author('Humberto A. Sanchez II')
        self._version = Version('1.0')

    def setOptions(self) -> bool:
        return True

    def doAction(self):

        selectedUmlShapes: UmlShapes = self._frameInformation.selectedUmlShapes

        layouts: LayoutAlgorithms = LayoutAlgorithms()
        defaultArranger: ArrangerType = self._preferences.defaultArranger
        if defaultArranger == ArrangerType.SPRING:
            layouts.applySpringLayout(umlFrame=self._frameInformation.umlFrame, umlShapes=selectedUmlShapes)
        elif defaultArranger == ArrangerType.ARF:
            layouts.applyArfLayout(umlFrame=self._frameInformation.umlFrame, umlShapes=selectedUmlShapes)
        elif defaultArranger == ArrangerType.PLANAR:
            layouts.applyPlanarLayout(umlFrame=self._frameInformation.umlFrame, umlShapes=selectedUmlShapes)
        elif defaultArranger == ArrangerType.FORCE_ATLAS2:
            layouts.applyForceAtlas2Layout(umlFrame=self._frameInformation.umlFrame, umlShapes=selectedUmlShapes)
        else:
            pass    # TODO User selects
