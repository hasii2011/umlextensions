from logging import Logger
from logging import getLogger

from umlextensions.IExtensionsFacade import IExtensionsFacade
from umlextensions.extensiontypes.ExtensionDataTypes import Author
from umlextensions.extensiontypes.ExtensionDataTypes import ExtensionDescription
from umlextensions.extensiontypes.ExtensionDataTypes import ExtensionName
from umlextensions.extensiontypes.ExtensionDataTypes import FileSuffix
from umlextensions.extensiontypes.ExtensionDataTypes import FormatName
from umlextensions.extensiontypes.ExtensionDataTypes import Version
from umlextensions.output.BaseOutputExtension import BaseOutputExtension
from umlextensions.output.OutputFormat import OutputFormat


FORMAT_NAME:            FormatName           = FormatName('GML')
FILE_SUFFIX:           FileSuffix           = FileSuffix('gml')
EXTENSION_DESCRIPTION: ExtensionDescription = ExtensionDescription('Graph Modeling Language - Portable Format for Graphs')

class OutputGML(BaseOutputExtension):

    def __init__(self, extensionsFacade: IExtensionsFacade):
        
        super().__init__(extensionsFacade=extensionsFacade)
        self.logger: Logger = getLogger(__name__)

        self._name    = ExtensionName('Python to UML')
        self._author  = Author('Humberto A. Sanchez II')
        self._version = Version('4.0')

        self._outputFormat  = OutputFormat(formatName=FORMAT_NAME, fileSuffix=FILE_SUFFIX, description=EXTENSION_DESCRIPTION)

    def setExportOptions(self) -> bool:
        return True

    def write(self) -> bool:
        return True
