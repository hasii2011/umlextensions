
from typing import cast

from logging import Logger
from logging import getLogger

from umlextensions.IExtensionsFacade import IExtensionsFacade

from umlextensions.extensiontypes.ExtensionDataTypes import Author
from umlextensions.extensiontypes.ExtensionDataTypes import ExtensionDescription
from umlextensions.extensiontypes.ExtensionDataTypes import ExtensionName
from umlextensions.extensiontypes.ExtensionDataTypes import FileSuffix
from umlextensions.extensiontypes.ExtensionDataTypes import FormatName
from umlextensions.extensiontypes.ExtensionDataTypes import Version
from umlextensions.extensiontypes.SingleFileRequestResponse import SingleFileRequestResponse

from umlextensions.output.OutputFormat import OutputFormat
from umlextensions.output.BaseOutputExtension import BaseOutputExtension


FORMAT_NAME:           FormatName           = FormatName('GML')
FILE_SUFFIX:           FileSuffix           = FileSuffix('gml')
EXTENSION_DESCRIPTION: ExtensionDescription = ExtensionDescription('Graph Modeling Language - Portable Format for Graphs')

class OutputGML(BaseOutputExtension):

    def __init__(self, extensionsFacade: IExtensionsFacade):
        
        super().__init__(extensionsFacade=extensionsFacade)
        self.logger: Logger = getLogger(__name__)

        self._name    = ExtensionName('UML to GML')
        self._author  = Author('Humberto A. Sanchez II')
        self._version = Version('4.0')

        self._outputFormat  = OutputFormat(formatName=FORMAT_NAME, fileSuffix=FILE_SUFFIX, description=EXTENSION_DESCRIPTION)

        self._exportResponse: SingleFileRequestResponse = cast(SingleFileRequestResponse, None)

    def setExportOptions(self) -> bool:

        defaultFileName: str = self._preferences.defaultGMLFilename

        self._exportResponse = self.askForFileToExport(defaultFileName=defaultFileName)

        if self._exportResponse.cancelled is True:
            return False
        else:
            return True

    def write(self) -> bool:
        return True
