
from typing import Tuple
from typing import cast

from logging import Logger
from logging import getLogger

from umlshapes.commands.shapemove.ShapeMoveInfo import MovedLinks
from umlshapes.commands.shapemove.ShapeMoveInfo import MovedShapes
from umlshapes.commands.shapemove.ShapeMoveRecorder import ShapeMoveRecorder
from umlshapes.commands.shapemove.ShapesMovedCommand import ShapesMovedCommand

from umlshapes.frames.UmlFrame import UmlFrame

from umlshapes.ShapeTypes import UmlShapes

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

        movedShapes: MovedShapes
        movedLinks:  MovedLinks
        movedShapes, movedLinks = self._recordInitialPositions(selectedUmlShapes=selectedUmlShapes)

        sugiyama: Sugiyama = Sugiyama(extensionsFacade=self._extensionsFacade, umlFrame=umlFrame)
        sugiyama.buildGraph(umlShapes=selectedUmlShapes)

        sugiyama.levelFind()
        sugiyama.addVirtualNodes()
        sugiyama.barycenter()

        # noinspection PyProtectedMember
        self.logger.info(f'Number of hierarchical intersections: {sugiyama._getNbIntersectAll()}')

        sugiyama.addNonHierarchicalNodes()
        sugiyama.assignCoordinates()

        self._submitShapesMovedCommand(movedShapes=movedShapes, movedLinks=movedLinks, umlFrame=umlFrame)

        self._extensionsFacade.extensionModifiedProject()
        self._extensionsFacade.refreshFrame()

        self.logger.info('End Sugiyama algorithm')

    def _recordInitialPositions(self, selectedUmlShapes: UmlShapes) -> Tuple[MovedShapes, MovedLinks]:
        """
        Record initial positions of selected shapes and attached links prior to running the layout.

        Args:
            selectedUmlShapes:  The selected shapes on the diagram

        Returns: A tuple containing the moved shapes and moved links dictionaries
        """
        movedShapes: MovedShapes = ShapeMoveRecorder.recordInitialShapePositions(umlShapes=selectedUmlShapes)
        movedLinks:  MovedLinks  = ShapeMoveRecorder.recordInitialLinkPositions(umlShapes=selectedUmlShapes)

        return movedShapes, movedLinks

    def _submitShapesMovedCommand(self, movedShapes: MovedShapes, movedLinks: MovedLinks, umlFrame: UmlFrame):
        """
        Construct and submit the ShapesMovedCommand once shapes are at their final positions.

        Args:
            movedShapes:  The initial and final positions of the shapes before and after layout
            movedLinks:   The initial and final intermediate bend and end positions of attached links
            umlFrame:     The active UML frame
        """
        self._shapesMovedCommand = ShapesMovedCommand(
            umlFrame=umlFrame,
            movedShapes=movedShapes,
            movedLinks=movedLinks,
            name='Sugiyama'
        )

        wasSuccessful: bool = umlFrame.commandProcessor.Submit(self._shapesMovedCommand)
        if not wasSuccessful:
            self.logger.warning('Sugiyama failed to record initial position')
