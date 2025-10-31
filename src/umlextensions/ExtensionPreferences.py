
from logging import Logger
from logging import getLogger

from codeallybasic.SecureConversions import SecureConversions

from codeallybasic.SingletonV3 import SingletonV3

from codeallybasic.DynamicConfiguration import Sections
from codeallybasic.DynamicConfiguration import KeyName
from codeallybasic.DynamicConfiguration import SectionName
from codeallybasic.DynamicConfiguration import ValueDescription
from codeallybasic.DynamicConfiguration import ValueDescriptions
from codeallybasic.DynamicConfiguration import DynamicConfiguration

MODULE_NAME:          str = 'umlextensions'
PREFERENCES_FILENAME: str = f'{MODULE_NAME}.ini'

SECTION_DEBUG: ValueDescriptions = ValueDescriptions(
    {
        KeyName('debugTempFileLocation'): ValueDescription(defaultValue='False', deserializer=SecureConversions.secureBoolean),
    }
)

EXTENSION_SECTIONS: Sections = Sections(
    {
        SectionName('Debug'): SECTION_DEBUG,
    }
)


class ExtensionPreferences(DynamicConfiguration, metaclass=SingletonV3):
    def __init__(self):
        self.logger: Logger = getLogger(__name__)

        super().__init__(baseFileName=f'{PREFERENCES_FILENAME}', moduleName=MODULE_NAME, sections=EXTENSION_SECTIONS)

        self._configParser.optionxform = str  # type: ignore
