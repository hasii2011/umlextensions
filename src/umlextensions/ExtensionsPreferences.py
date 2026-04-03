
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
from umlshapes.types.UmlPosition import UmlPosition

from umlextensions.tools.diagramarranger.ForceDirectedMethod import ForceDirectedMethod
from umlextensions.tools.orthogonallayout.LayoutAreaDimensions import LayoutAreaDimensions

MODULE_NAME:          str = 'umlextensions'
PREFERENCES_FILENAME: str = f'{MODULE_NAME}.ini'

DEFAULT_ORTHOGONAL_LAYOUT_SIZE:     LayoutAreaDimensions = LayoutAreaDimensions(512, 512)
DEFAULT_ORTHOGONAL_LAYOUT_SIZE_STR: str                  = str(DEFAULT_ORTHOGONAL_LAYOUT_SIZE)

DEFAULT_ORTHOGONAL_LAYOUT_TOP_LEFT:     UmlPosition = UmlPosition(x=25, y=25)
DEFAULT_ORTHOGONAL_LAYOUT_TOP_LEFT_STR: str         = str(DEFAULT_ORTHOGONAL_LAYOUT_TOP_LEFT)

DEFAULT_SPRING_LAYOUT_CENTER:     UmlPosition = UmlPosition(x=800, y=600)
DEFAULT_SPRING_LAYOUT_CENTER_STR: str         = str(DEFAULT_SPRING_LAYOUT_CENTER)
DEFAULT_SPRING_LAYOUT_METHOD:     str         = ForceDirectedMethod.ENERGY.value

SECTION_EXTENSIONS: ValueDescriptions = ValueDescriptions(
    {
        KeyName('sugiyamaStepByStep'):      ValueDescription(defaultValue='False', deserializer=SecureConversions.secureBoolean),
        KeyName('defaultGMLFilename'):      ValueDescription(defaultValue='GmlDump.gml'),
        KeyName('orthogonalLayoutSize'):    ValueDescription(defaultValue=DEFAULT_ORTHOGONAL_LAYOUT_SIZE_STR,     deserializer=LayoutAreaDimensions.deSerialize),
        KeyName('orthogonalLayoutTopLeft'): ValueDescription(defaultValue=DEFAULT_ORTHOGONAL_LAYOUT_TOP_LEFT_STR, deserializer=UmlPosition.deSerialize),
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

SECTION_SPRING_LAYOUT: ValueDescriptions = ValueDescriptions(
    {
        KeyName('iterations'):          ValueDescription(defaultValue='50',    deserializer=SecureConversions.secureInteger),
        KeyName('optimalNodeDistance'): ValueDescription(defaultValue='300.0', deserializer=SecureConversions.secureFloat),
        KeyName('layoutCenter'): ValueDescription(defaultValue=DEFAULT_SPRING_LAYOUT_CENTER_STR, deserializer=UmlPosition.deSerialize),
        KeyName('layoutMethod'): ValueDescription(defaultValue=DEFAULT_SPRING_LAYOUT_METHOD,     deserializer=ForceDirectedMethod),
    }
    #         KeyName('backGroundColor'):         ValueDescription(defaultValue=DEFAULT_BACKGROUND_COLOR, enumUseValue=True, deserializer=UmlColor),
)
SECTION_DEBUG: ValueDescriptions = ValueDescriptions(
    {
        KeyName('autoSelectAll'):         ValueDescription(defaultValue='True',  deserializer=SecureConversions.secureBoolean),
        KeyName('debugTempFileLocation'): ValueDescription(defaultValue='False', deserializer=SecureConversions.secureBoolean),
    }
)

EXTENSION_SECTIONS: Sections = Sections(
    {
        SectionName('Extensions'):    SECTION_EXTENSIONS,
        SectionName('Features'):      SECTION_FEATURES,
        SectionName('Shape Layout'):  SECTION_SHAPE_LAYOUT,
        SectionName('Spring Layout'): SECTION_SPRING_LAYOUT,
        SectionName('Debug'):         SECTION_DEBUG,
    }
)


class ExtensionsPreferences(DynamicConfiguration, metaclass=SingletonV3):
    def __init__(self):
        self._logger: Logger = getLogger(__name__)

        super().__init__(baseFileName=f'{PREFERENCES_FILENAME}', moduleName=MODULE_NAME, sections=EXTENSION_SECTIONS)

        self._configParser.optionxform = str  # type: ignore
