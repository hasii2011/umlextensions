
from typing import cast

from logging import Logger
from logging import getLogger

from abc import ABC
from abc import abstractmethod

from umlextensions.ExtensionsTypes import FrameInformation
from umlextensions.IExtensionsFacade import IExtensionsFacade

from umlextensions.extensiontypes.BaseExtension import BaseExtension
from umlextensions.extensiontypes.ExtensionDataTypes import UNSPECIFIED_DESCRIPTION
from umlextensions.extensiontypes.ExtensionDataTypes import UNSPECIFIED_FILE_SUFFIX
from umlextensions.extensiontypes.ExtensionDataTypes import UNSPECIFIED_NAME

from umlextensions.output.OutputFormat import OutputFormat


class BaseOutputExtension(BaseExtension, ABC):
    """
        Base class for extensions that can convert UML Diagrams into foreign
        structured data.  Examples include but are not limited to:

        * Mermaid
        * PDF
        * Images (png, jpg, bmp, etc
        * Generate Python code
        * Generate Java code

    """
    def __init__(self, extensionsFacade: IExtensionsFacade):

        super().__init__(extensionsFacade)
        self.logger: Logger = getLogger(__name__)

        self._outputFormat:     OutputFormat     = OutputFormat(formatName=UNSPECIFIED_NAME, fileSuffix=UNSPECIFIED_FILE_SUFFIX, description=UNSPECIFIED_DESCRIPTION)
        self._frameInformation: FrameInformation = cast(FrameInformation, None)

    @property
    def outputFormat(self) -> OutputFormat:
        return self._outputFormat

    def executeExport(self):
        """
        Called by the extension manager to begin the export process.
        """
        # noinspection PyTypeChecker
        self._extensionsFacade.requestCurrentFrameInformation(callback=self._executeExport)   # type ignore

    def _executeExport(self, frameInformation: FrameInformation):
        """
        The callback necessary to start the export process;

        Args:
            frameInformation:
        """
        assert self._outputFormat.formatName != UNSPECIFIED_NAME,         'Developer error. We cannot export w/o an export format name'
        assert self._outputFormat.fileSuffix != UNSPECIFIED_FILE_SUFFIX,  'Developer error. We cannot export w/o an export file suffix'
        assert self._outputFormat.description != UNSPECIFIED_DESCRIPTION, 'Developer error. We cannot export w/o an export description'

        self._frameInformation = frameInformation

        if self._requireActiveFrame is True:
            if frameInformation.frameActive is False:
                self.showNoUmlFrameDialog()
                return
        if self.setExportOptions() is True:
            self.write()

    @abstractmethod
    def setExportOptions(self) -> bool:
        """
        Prepare for the export.
        Use this method to query the end-user for any additional export options

        Returns:
            if False, the export is cancelled
        """
        pass

    @abstractmethod
    def write(self) -> bool:
        """
        Write data from a file;  Presumably, the file was specified on the call
        to setExportOptions
        """
        pass
