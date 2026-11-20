
from logging import Logger
from logging import getLogger

from codeallybasic.DynamicConfiguration import DynamicConfiguration
from codeallybasic.DynamicConfiguration import KeyName
from codeallybasic.DynamicConfiguration import SectionName
from codeallybasic.DynamicConfiguration import Sections
from codeallybasic.DynamicConfiguration import ValueDescription
from codeallybasic.DynamicConfiguration import ValueDescriptions
from codeallybasic.SecureConversions import SecureConversions
from codeallybasic.SingletonV3 import SingletonV3

from umlextensions.tools.sugiyama.SugiyamaConstants import DEFAULT_HORIZONTAL_SPACING
from umlextensions.tools.sugiyama.SugiyamaConstants import DEFAULT_LEFT_MARGIN
from umlextensions.tools.sugiyama.SugiyamaConstants import DEFAULT_TOP_MARGIN
from umlextensions.tools.sugiyama.SugiyamaConstants import DEFAULT_VERTICAL_SPACING

MODULE_NAME:                   str = 'sugiyama'
SUGIYAMA_PREFERENCES_FILENAME: str = 'sugiyama.ini'

SECTION_SUGIYAMA_LAYOUT: ValueDescriptions = ValueDescriptions(
    {
        KeyName('leftMargin'):         ValueDescription(defaultValue=str(DEFAULT_LEFT_MARGIN),       deserializer=SecureConversions.secureInteger),
        KeyName('topMargin'):          ValueDescription(defaultValue=str(DEFAULT_TOP_MARGIN),        deserializer=SecureConversions.secureInteger),
        KeyName('horizontalSpacing'): ValueDescription(defaultValue=str(DEFAULT_HORIZONTAL_SPACING), deserializer=SecureConversions.secureInteger),
        KeyName('verticalSpacing'):   ValueDescription(defaultValue=str(DEFAULT_VERTICAL_SPACING),   deserializer=SecureConversions.secureInteger),
        KeyName('sugiyamaStepByStep'): ValueDescription(defaultValue='False',                        deserializer=SecureConversions.secureBoolean),
    }
)

SUGIYAMA_SECTIONS: Sections = Sections(
    {
        SectionName('Sugiyama Layout'): SECTION_SUGIYAMA_LAYOUT,
    }
)


class SugiyamaPreferences(DynamicConfiguration, metaclass=SingletonV3):
    """
    Dedicated runtime preferences for the Sugiyama automatic layout algorithm.

    Persisted separately in sugiyama.ini via DynamicConfiguration to remain
    independent of the general ExtensionsPreferences.
    """

    def __init__(self):
        self._logger: Logger = getLogger(__name__)

        super().__init__(
            baseFileName=SUGIYAMA_PREFERENCES_FILENAME,
            moduleName=MODULE_NAME,
            sections=SUGIYAMA_SECTIONS,
        )

        self._configParser.optionxform = str  # type: ignore
