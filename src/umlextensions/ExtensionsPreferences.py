
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
from umlshapes.types.UmlColor import UmlColor
from umlshapes.types.UmlFontFamily import UmlFontFamily
from umlshapes.types.UmlPosition import UmlPosition

from umlextensions.tools.diagramarranger.ArrangerType import ArrangerType
from umlextensions.tools.diagramarranger.configpanels.ForceDirectedMethod import ForceDirectedMethod
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

MIN_ARF_SPRING_STRENGTH: float = 1.1
MAX_ARF_SPRING_STRENGTH: float = 100.0
MIN_ITERATION_STEP_SIZE: float = 0.001
MAX_ITERATION_STEP_SIZE: float = 0.9

DEFAULT_ARRANGER: ArrangerType = ArrangerType.SPRING

DEFAULT_TIP_TITLE_TEXT_COLOR: str = UmlColor.BLACK.value
DEFAULT_TIP_TEXT_COLOR:       str = UmlColor.BLACK.value
DEFAULT_BALLOON_COLOR:        str = UmlColor.LIGHT_YELLOW.value



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
        KeyName('iterations'):           ValueDescription(defaultValue='50',    deserializer=SecureConversions.secureInteger),
        KeyName('frameSizeScaleFactor'): ValueDescription(defaultValue='400',   deserializer=SecureConversions.secureInteger),
        KeyName('optimalNodeDistance'):  ValueDescription(defaultValue='300.0', deserializer=SecureConversions.secureFloat),
        KeyName('layoutMethod'): ValueDescription(defaultValue=DEFAULT_SPRING_LAYOUT_METHOD,     deserializer=ForceDirectedMethod),
    }
)

SECTION_ARF_LAYOUT: ValueDescriptions = ValueDescriptions(
    {
        KeyName('arfMaxIterations'):    ValueDescription(defaultValue='1000',  deserializer=SecureConversions.secureInteger),
        KeyName('arfFrameScaleFactor'): ValueDescription(defaultValue='400',   deserializer=SecureConversions.secureInteger),
        KeyName('arfSpringStrength'): ValueDescription(defaultValue=str(MIN_ARF_SPRING_STRENGTH), deserializer=SecureConversions.secureFloat),
        KeyName('iterationStepSize'): ValueDescription(defaultValue=str(MIN_ITERATION_STEP_SIZE), deserializer=SecureConversions.secureFloat),
    }
)

SECTION_PLANAR_LAYOUT: ValueDescriptions = ValueDescriptions(
    {
        KeyName('planarFrameScaleFactor'): ValueDescription(defaultValue='300', deserializer=SecureConversions.secureInteger),
        KeyName('positionsScale'):         ValueDescription(defaultValue='1',   deserializer=SecureConversions.secureInteger),
    }

)

SECTION_FORCE_ATLAS2_LAYOUT: ValueDescriptions = ValueDescriptions(
    {
        KeyName('atlasMaxIterations'):    ValueDescription(defaultValue='100',    deserializer=SecureConversions.secureInteger),
        KeyName('jitterTolerance'):       ValueDescription(defaultValue='1.0',    deserializer=SecureConversions.secureFloat),
        KeyName('scalingRatio'):          ValueDescription(defaultValue='2.0',    deserializer=SecureConversions.secureFloat),
        KeyName('gravity'):               ValueDescription(defaultValue='1.0',    deserializer=SecureConversions.secureFloat),
        KeyName('distributedAction'):     ValueDescription(defaultValue='False',  deserializer=SecureConversions.secureBoolean),
        KeyName('strongGravity'):         ValueDescription(defaultValue='False',  deserializer=SecureConversions.secureBoolean),
        KeyName('logarithmicAttraction'): ValueDescription(defaultValue='False',  deserializer=SecureConversions.secureBoolean),
        KeyName('preventShapeCrowding'):  ValueDescription(defaultValue='False', deserializer=SecureConversions.secureBoolean),
    }
)

SECTION_ARRANGER_COMMON: ValueDescriptions = ValueDescriptions(
    {
        KeyName('layoutCenter'):    ValueDescription(defaultValue=DEFAULT_SPRING_LAYOUT_CENTER_STR, deserializer=UmlPosition.deSerialize),
        KeyName('defaultArranger'): ValueDescription(defaultValue=str(DEFAULT_ARRANGER), deserializer=ArrangerType),
    }
)
SECTION_ARRANGER_TOOLTIP: ValueDescriptions = ValueDescriptions(
    {
        KeyName('balloonColor'): ValueDescription(defaultValue=DEFAULT_BALLOON_COLOR, enumUseValue=True, deserializer=UmlColor),

        KeyName('balloonTipTitleFontSize'):   ValueDescription(defaultValue='18',    deserializer=SecureConversions.secureInteger),
        KeyName('balloonTipTitleBold'):       ValueDescription(defaultValue='True',  deserializer=SecureConversions.secureBoolean),
        KeyName('balloonTipTitleItalicize'):  ValueDescription(defaultValue='False', deserializer=SecureConversions.secureBoolean),
        KeyName('balloonTipTitleFontFamily'): ValueDescription(defaultValue='Swiss', deserializer=UmlFontFamily.deSerialize),
        KeyName('balloonTipTitleColor'):      ValueDescription(defaultValue=DEFAULT_TIP_TITLE_TEXT_COLOR, enumUseValue=True, deserializer=UmlColor),

        KeyName('balloonTipTextFontSize'):   ValueDescription(defaultValue='14',    deserializer=SecureConversions.secureInteger),
        KeyName('balloonTipTextBold'):       ValueDescription(defaultValue='False', deserializer=SecureConversions.secureBoolean),
        KeyName('balloonTipTextItalicize'):  ValueDescription(defaultValue='False', deserializer=SecureConversions.secureBoolean),
        KeyName('balloonTipTextFontFamily'): ValueDescription(defaultValue='Swiss', deserializer=UmlFontFamily.deSerialize),
        KeyName('balloonTipTextColor'):      ValueDescription(defaultValue=DEFAULT_TIP_TEXT_COLOR, enumUseValue=True, deserializer=UmlColor),

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
        SectionName('Extensions'):          SECTION_EXTENSIONS,
        SectionName('Features'):            SECTION_FEATURES,
        SectionName('Shape Layout'):        SECTION_SHAPE_LAYOUT,
        SectionName('Spring Layout'):       SECTION_SPRING_LAYOUT,
        SectionName('ARF Layout'):          SECTION_ARF_LAYOUT,
        SectionName('Planar Layout'):       SECTION_PLANAR_LAYOUT,
        SectionName('Force Atlas2 Layout'): SECTION_FORCE_ATLAS2_LAYOUT,
        SectionName('Arranger Common'):     SECTION_ARRANGER_COMMON,
        SectionName('ArrangerTooltip'):     SECTION_ARRANGER_TOOLTIP,
        SectionName('Debug'):               SECTION_DEBUG,
    }
)


class ExtensionsPreferences(DynamicConfiguration, metaclass=SingletonV3):
    def __init__(self):
        self._logger: Logger = getLogger(__name__)

        super().__init__(baseFileName=f'{PREFERENCES_FILENAME}', moduleName=MODULE_NAME, sections=EXTENSION_SECTIONS)

        self._configParser.optionxform = str  # type: ignore
