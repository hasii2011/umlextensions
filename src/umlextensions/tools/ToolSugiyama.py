
from typing import cast

from logging import Logger
from logging import getLogger

from umlshapes.commands.ShapesMovedCommand import ShapesMovedCommand

from umlshapes.frames.UmlFrame import UmlFrame
from umlshapes.frames.ShapeMoveInfo import ShapeId
from umlshapes.frames.ShapeMoveInfo import InitialPositions

from umlshapes.ShapeTypes import UmlShapes
from umlshapes.links.UmlLink import UmlLink
from umlshapes.ShapeTypes import UmlShapeGenre
from umlshapes.links.UmlLinkLabel import UmlLinkLabel

from umlextensions.IExtensionsFacade import IExtensionsFacade

from umlextensions.extensiontypes.ExtensionDataTypes import Author
from umlextensions.extensiontypes.ExtensionDataTypes import Version
from umlextensions.extensiontypes.ExtensionDataTypes import ExtensionName

from umlextensions.tools.sugiyama.Sugiyama import Sugiyama
from umlextensions.tools.BaseToolExtension import BaseToolExtension


class ToolSugiyama(BaseToolExtension):

    def __init__(self, extensionsFacade: IExtensionsFacade):

        super().__init__(extensionsFacade=extensionsFacade)
        self.logger: Logger = getLogger(__name__)

        self._name      = ExtensionName('Sugiyama Automatic Layout')
        self._author    = Author('Nicolas Dubois <nicdub@gmx.ch>')
        self._version   = Version('1.1')

        self._autoSelectAll = False

        self._shapesMovedCommand: ShapesMovedCommand = cast(ShapesMovedCommand, None)   # noqa

    def setOptions(self) -> bool:
        """
        Prepare for the tool action.
        This can be used to ask some questions to the user.

        Returns: If False, the import should be canceled.  'True' to proceed
        """
        return True

    def doAction(self):

        self.logger.info('Begin Sugiyama algorithm')

        selectedUmlShapes: UmlShapes = self._frameInformation.selectedUmlShapes
        umlFrame:          UmlFrame  = self._frameInformation.umlFrame

        initialPositions: InitialPositions = self._recordInitialPositions(selectedUmlShapes=selectedUmlShapes, umlFrame=umlFrame)

        sugiyama: Sugiyama = Sugiyama(extensionsFacade=self._extensionsFacade, umlFrame=umlFrame)
        sugiyama.createInterfaceUmlShapeLayout(umlShapes=selectedUmlShapes)

        sugiyama.levelFind()
        sugiyama.addVirtualNodes()
        sugiyama.barycenter()

        # noinspection PyProtectedMember
        self.logger.info(f'Number of hierarchical intersections: {sugiyama._getNbIntersectAll()}')

        sugiyama.addNonHierarchicalNodes()
        sugiyama.fixPositions()

        self._submitShapesMovedCommand(initialPositions=initialPositions, umlFrame=umlFrame)

        self._extensionsFacade.extensionModifiedProject()
        self._extensionsFacade.refreshFrame()

        self.logger.info('End Sugiyama algorithm')

    def _recordInitialPositions(self, selectedUmlShapes: UmlShapes, umlFrame: UmlFrame) -> InitialPositions:
        """
        Record initial positions of selected shapes prior to running the layout.

        Args:
            selectedUmlShapes:  The selected shapes on the diagram
            umlFrame:           The active UML frame

        Returns: The dictionary of shape IDs to their starting positions
        """
        initialPositions: InitialPositions = InitialPositions({})

        for shape in selectedUmlShapes:

            umlShape: UmlShapeGenre = cast(UmlShapeGenre, shape)

            if not isinstance(umlShape, UmlLink) and not isinstance(umlShape, UmlLinkLabel):
                initialPositions[ShapeId(umlShape.id)] = umlShape.position
                umlFrame.markShapeAsMoved(umlShape)

        return initialPositions

    def _submitShapesMovedCommand(self, initialPositions: InitialPositions, umlFrame: UmlFrame):
        """
        Construct and submit the ShapesMovedCommand once shapes are at their final positions.

        Args:
            initialPositions:  The initial positions of the shapes before layout
            umlFrame:          The active UML frame
        """
        self._shapesMovedCommand = ShapesMovedCommand(
            umlFrame=umlFrame,
            movedShapes=umlFrame.movedShapes,
            initialPositions=initialPositions,
            name='Sugiyama'
        )

        wasSuccessful: bool = umlFrame.commandProcessor.Submit(self._shapesMovedCommand)
        if not wasSuccessful:
            self.logger.warning('Sugiyama failed to record initial position')

        umlFrame.clearMovedShapes()
