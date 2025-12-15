
from typing import cast

from logging import Logger
from logging import getLogger

from os import linesep as osLineSep

from wx import OK
from wx import ICON_ERROR
from wx import MessageDialog

from umlmodel.enumerations.LinkType import LinkType

from umlshapes.ShapeTypes import UmlLinkGenre

from umlextensions.Common import NO_PARENT_WINDOW

from umlextensions.IExtensionsFacade import IExtensionsFacade
from umlextensions.extensiontypes.ExtensionDataTypes import Author
from umlextensions.extensiontypes.ExtensionDataTypes import ExtensionName
from umlextensions.extensiontypes.ExtensionDataTypes import Version

from umlextensions.tools.BaseToolExtension import BaseToolExtension
from umlextensions.tools.orthogonalrouting.DlgDiagnoseLayout import DlgDiagnoseLayout
from umlextensions.tools.orthogonalrouting.DlgOrthogonalRoutingConfiguration import DlgOrthogonalRoutingConfiguration
from umlextensions.tools.orthogonalrouting.OrthogonalConnectorAdapter import OrthogonalConnectorAdapter


class ToolOrthogonalRouting(BaseToolExtension):

    def __init__(self, extensionsFacade: IExtensionsFacade):

        super().__init__(extensionsFacade=extensionsFacade)
        self.logger: Logger = getLogger(__name__)

        self._name      = ExtensionName('Orthogonal Automatic Layout')
        self._author    = Author('Humberto A. Sanchez III')
        self._version   = Version('2.0')

    def setOptions(self) -> bool:
        """
        Prepare for the tool action.
        This can be used to ask some questions to the user.

        Returns: If False, the import should be cancelled.  'True' to proceed
        """
        with DlgOrthogonalRoutingConfiguration(NO_PARENT_WINDOW, extensionsFacade=self._extensionsFacade) as dlg:
            if dlg.ShowModal() == OK:
                return True
            else:
                self.logger.warning(f'Cancelled')
                return False

    def doAction(self):

        self.logger.info(f'Begin Orthogonal Routing')
        self._extensionsFacade.getSelectedUmlShapes(callback=self._doAction)
        self.logger.info('End Orthogonal Routing')

    def _doAction(self, selectedUmlShapes):
        self.logger.info(f'_doAction')

        adapter: OrthogonalConnectorAdapter = OrthogonalConnectorAdapter(extensionsFacade=self._extensionsFacade)

        umlLink: UmlLinkGenre = cast(UmlLinkGenre, None)

        for potentialLink in selectedUmlShapes:
            if isinstance(potentialLink, UmlLinkGenre):
                try:
                    umlLink = cast(UmlLinkGenre, potentialLink)
                    success: bool = adapter.runConnector(oglLink=umlLink)
                    if success is False:
                        message: str           = self._composeGoodErrorMessage(umlLink)
                        booBoo:  MessageDialog = MessageDialog(parent=None, message=message, caption='No orthogonal route', style=OK | ICON_ERROR)
                        booBoo.ShowModal()
                        if self._preferences.diagnoseOrthogonalRouter is True:

                            dlg: DlgDiagnoseLayout    = DlgDiagnoseLayout(parent=None)
                            dlg.extensionsFacade      = self._extensionsFacade
                            dlg.diagnosticInformation = adapter.diagnosticInformation
                            dlg.Show(True)
                        break

                except (AttributeError, TypeError) as e:
                    self.logger.error(f'{e} - {umlLink=}')

    def _composeGoodErrorMessage(self, oglLink: UmlLinkGenre) -> str:

        linkType: LinkType = oglLink.modelLink.linkType
        message: str = (
            f'Could not find an orthogonal route for link: {linkType}{osLineSep}'
            f'from {osLineSep}'
            f'{oglLink.sourceShape} {osLineSep}' 
            f'to{osLineSep}'
            f'{oglLink.destinationShape}'
        )

        return message
