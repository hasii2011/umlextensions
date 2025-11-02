
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

SECTION_FEATURES: ValueDescriptions = ValueDescriptions(
    {
        KeyName('startDirectory'):           ValueDescription(defaultValue=''),
    }
)

SECTION_DEBUG: ValueDescriptions = ValueDescriptions(
    {
        KeyName('autoSelectAll'): ValueDescription(defaultValue='True', deserializer=SecureConversions.secureBoolean),
    }
)

EXTENSION_SECTIONS: Sections = Sections(
    {
        SectionName('Features'): SECTION_FEATURES,
        SectionName('Debug'):    SECTION_DEBUG,
    }
)


class ExtensionsPreferences(DynamicConfiguration, metaclass=SingletonV3):
    def __init__(self):
        self._logger: Logger = getLogger(__name__)

        super().__init__(baseFileName=f'{PREFERENCES_FILENAME}', moduleName=MODULE_NAME, sections=EXTENSION_SECTIONS)

        self._configParser.optionxform = str  # type: ignore
