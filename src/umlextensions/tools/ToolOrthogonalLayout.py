
from typing import cast

from logging import Logger
from logging import getLogger

from wx import OK
from wx import MessageBox
from wx import ICON_ERROR

from umlshapes.ShapeTypes import UmlShapes

from umlshapes.shapes.UmlNote import UmlNote
from umlshapes.shapes.UmlClass import UmlClass

from umlextensions.IExtensionsFacade import IExtensionsFacade

from umlshapes.mixins.TopLeftMixin import TopLeftMixin

from umlshapes.types.UmlPosition import UmlPosition

from umlextensions.extensiontypes.ExtensionDataTypes import Author
from umlextensions.extensiontypes.ExtensionDataTypes import Version
from umlextensions.extensiontypes.ExtensionDataTypes import ExtensionName

from umlextensions.tools.orthogonallayout.OrthogonalAdapter import OrthogonalAdapter
from umlextensions.tools.orthogonallayout.OrthogonalAdapter import UmlShapeCoordinate
from umlextensions.tools.orthogonallayout.OrthogonalAdapter import UmlShapeCoordinates
from umlextensions.tools.orthogonallayout.OrthogonalAdapterException import OrthogonalAdapterException

from umlextensions.tools.orthogonallayout.DlgLayoutDimensions import DlgLayoutDimensions
from umlextensions.tools.orthogonallayout.LayoutAreaDimensions import LayoutAreaDimensions

from umlextensions.tools.BaseToolExtension import BaseToolExtension


class ToolOrthogonalLayout(BaseToolExtension):

    def __init__(self, extensionsFacade: IExtensionsFacade):

        super().__init__(extensionsFacade=extensionsFacade)

        self.logger: Logger = getLogger(__name__)

        self._name    = ExtensionName('Orthogonal Layout')
        self._author  = Author('Humberto A. Sanchez II')
        self._version = Version('3.0')

        self._layoutWidth:  int = 0
        self._layoutHeight: int = 0

    def setOptions(self) -> bool:
        with DlgLayoutDimensions(None) as dlg:    # noqa
            if dlg.ShowModal() == OK:
                self.logger.warning(f'Retrieved data: layoutWidth: {dlg.layoutWidth} layoutHeight: {dlg.layoutHeight}')
                self._layoutWidth  = dlg.layoutWidth
                self._layoutHeight = dlg.layoutHeight
                proceed: bool = True
            else:
                self.logger.info(f'Cancelled')
                proceed = False

        return proceed

    def doAction(self):
        self.logger.info(f'Begin Orthogonal Layout')
        selectedUmlShapes = self._frameInformation.selectedUmlShapes
        try:
            orthogonalAdapter: OrthogonalAdapter = OrthogonalAdapter(umlShapes=selectedUmlShapes)

            layoutAreaSize: LayoutAreaDimensions = LayoutAreaDimensions(self._layoutWidth, self._layoutHeight)
            orthogonalAdapter.doLayout(layoutAreaSize)
        except OrthogonalAdapterException as oae:
            MessageBox(f'{oae}', 'Error', OK | ICON_ERROR)
            return

        if orthogonalAdapter is not None:
            self._reLayoutNodes(selectedUmlShapes, orthogonalAdapter.umlShapeCoordinates)

            self._extensionsFacade.wiggleShapes()
            self._extensionsFacade.extensionModifiedProject()

        self.logger.info('End Orthogonal Layout')

    def _reLayoutNodes(self, umlObjects: UmlShapes, umlShapeCoordinates: UmlShapeCoordinates):
        """

        Args:
            umlObjects:
        """
        handledShapes = {UmlClass, UmlNote}
        for umlObj in umlObjects:
            if type(umlObj) in handledShapes:
                if isinstance(umlObj, UmlClass):
                    umlName: str = umlObj.modelClass.name
                else:
                    umlName = cast(UmlNote, umlObj).modelNote.name

                umlShapeCoordinate: UmlShapeCoordinate = umlShapeCoordinates[umlName]

                self._moveShape(cast(TopLeftMixin, umlObj), umlShapeCoordinate)      # noqas

    def _moveShape(self, srcShape: TopLeftMixin, umlCoordinate: UmlShapeCoordinate):
        """

        Args:
            srcShape:
            umlCoordinate:
        """

        oldPosition: UmlPosition = srcShape.position

        umlPosition: UmlPosition = self._preferences.orthogonalLayoutTopLeft
        newPosition: UmlPosition = UmlPosition(x=umlCoordinate.x + umlPosition.x, y=umlCoordinate.y + umlPosition.y)
        self.logger.info(f'{srcShape} - {oldPosition=}  {newPosition=}')

        srcShape.position = newPosition
