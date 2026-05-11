
from typing import cast

from logging import Logger
from logging import getLogger

from umlshapes.frames.ShapeMoveInfo import ShapeId
from umlshapes.frames.ShapeMoveInfo import InitialPositions

from umlshapes.ShapeTypes import UmlShapes

from umlshapes.commands.ShapesMovedCommand import ShapesMovedCommand

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

        self._initialPositions:  InitialPositions = InitialPositions({})

        self._shapesMovedCommand: ShapesMovedCommand = cast(ShapesMovedCommand, None)   # noqa

    def setOptions(self) -> bool:
        return True

    def doAction(self):

        from umlshapes.frames.UmlFrame import UmlFrame
        from umlshapes.ShapeTypes import UmlShapeGenre
        from umlshapes.links.UmlLink import UmlLink
        from umlshapes.links.UmlLinkLabel import UmlLinkLabel

        umlFrame: UmlFrame = self._frameInformation.umlFrame

        shapes = umlFrame.selectedShapes
        for s in shapes:
            umlShape: UmlShapeGenre = cast(UmlShapeGenre, s)
            if not isinstance(umlShape, UmlLink) and not isinstance(umlShape, UmlLinkLabel):
                self._initialPositions[ShapeId(umlShape.id)] = umlShape.position
                umlFrame.markShapeAsMoved(umlShape)

        self._shapesMovedCommand = ShapesMovedCommand(
            umlFrame=umlFrame,
            movedShapes=umlFrame.movedShapes,
            initialPositions=self._initialPositions
        )

        umlFrame.commandProcessor.Submit(self._shapesMovedCommand)
        mysticAdapter: MysticAdapter = MysticAdapter(
            parent=umlFrame,
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
        self._shapesMovedCommand.Undo()
