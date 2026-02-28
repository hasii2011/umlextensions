
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

from umlextensions.tools.orthogonallayout.LayoutAreaDimensions import LayoutAreaDimensions

MODULE_NAME:          str = 'umlextensions'
PREFERENCES_FILENAME: str = f'{MODULE_NAME}.ini'

DEFAULT_ORTHOGONAL_LAYOUT_SIZE:     LayoutAreaDimensions   = LayoutAreaDimensions(512, 512)
DEFAULT_ORTHOGONAL_LAYOUT_SIZE_STR: str              = DEFAULT_ORTHOGONAL_LAYOUT_SIZE.__str__()

SECTION_EXTENSIONS: ValueDescriptions = ValueDescriptions(
    {
        KeyName('sugiyamaStepByStep'): ValueDescription(defaultValue='False', deserializer=SecureConversions.secureBoolean),
        KeyName('defaultGMLFilename'): ValueDescription(defaultValue='GmlDump.gml'),
        KeyName('orthogonalLayoutSize'): ValueDescription(defaultValue=DEFAULT_ORTHOGONAL_LAYOUT_SIZE_STR, deserializer=LayoutAreaDimensions.deSerialize),

    }
)

SECTION_FEATURES: ValueDescriptions = ValueDescriptions(
    {
        KeyName('startDirectory'):           ValueDescription(defaultValue=''),
        KeyName('diagnoseOrthogonalRouter'): ValueDescription(defaultValue='True', deserializer=SecureConversions.secureBoolean),
    }
)

SECTION_SHAPE_LAYOUT: ValueDescriptions = ValueDescriptions(
    {
        KeyName('startX'):     ValueDescription(defaultValue='20',   deserializer=SecureConversions.secureInteger),
        KeyName('startY'):     ValueDescription(defaultValue='20',   deserializer=SecureConversions.secureInteger),
        KeyName('xIncrement'): ValueDescription(defaultValue='20',   deserializer=SecureConversions.secureInteger),
        KeyName('maximumX'):   ValueDescription(defaultValue='3000', deserializer=SecureConversions.secureInteger),
    }
)

SECTION_DEBUG: ValueDescriptions = ValueDescriptions(
    {
        KeyName('autoSelectAll'):         ValueDescription(defaultValue='True',  deserializer=SecureConversions.secureBoolean),
        KeyName('debugTempFileLocation'): ValueDescription(defaultValue='False', deserializer=SecureConversions.secureBoolean),
    }
)

EXTENSION_SECTIONS: Sections = Sections(
    {
        SectionName('Extensions'):   SECTION_EXTENSIONS,
        SectionName('Features'):     SECTION_FEATURES,
        SectionName('Shape Layout'): SECTION_SHAPE_LAYOUT,
        SectionName('Debug'):        SECTION_DEBUG,
    }
)


class ExtensionsPreferences(DynamicConfiguration, metaclass=SingletonV3):
    def __init__(self):
        self._logger: Logger = getLogger(__name__)

        super().__init__(baseFileName=f'{PREFERENCES_FILENAME}', moduleName=MODULE_NAME, sections=EXTENSION_SECTIONS)

        self._configParser.optionxform = str  # type: ignore
