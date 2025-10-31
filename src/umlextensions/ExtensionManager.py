
from typing import Callable
from typing import cast
from typing import Dict
from typing import List
from typing import NewType

from logging import Logger
from logging import getLogger

from enum import Enum

from dataclasses import field
from dataclasses import dataclass

from wx import ICON_ERROR
from wx import MessageDialog
from wx import NewIdRef
from wx import OK

from umlextensions.ExtensionPreferences import ExtensionPreferences
from umlextensions.extensiontypes.ExtensionDataTypes import ExtensionName
from umlextensions.input.BaseInputExtension import BaseInputExtension

# Return type from wx.NewIdRef()
WindowId = NewType('WindowId', int)

#
#  Both of these hold the class extension types for the Extension classes
#
ExtensionList  = NewType('ExtensionList',  List[type])
ExtensionIDMap = NewType('ExtensionIDMap', Dict[WindowId, type])

def createExtensionIdMapFactory() -> ExtensionIDMap:
    return ExtensionIDMap({})

class ExtensionMapType(Enum):
    INPUT_MAP  = 'InputMap'
    OUTPUT_MAP = 'OutputMap'
    TOOL_MAP   = 'ToolMap'
    NONE       = 'None'

#
# Some nice syntactic sugar
#
@dataclass
class BasePluginMap:
    mapType:        ExtensionMapType = ExtensionMapType.NONE
    extensionIdMap: ExtensionIDMap   = field(default_factory=createExtensionIdMapFactory)

@dataclass
class InputExtensionMap(BasePluginMap):
    def __init__(self):
        super().__init__()
        self.mapType = ExtensionMapType.INPUT_MAP

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f'{self.mapType} plugin count: {len(self.extensionIdMap)}'


INPUT_EXTENSIONS: ExtensionList = ExtensionList(
    []
)

@dataclass
class ExtensionDetails:
    name:    ExtensionName = ExtensionName('')
    author:  str = ''
    version: str = ''

class ExtensionManager:
    """
    Manages the various extensions provided by this module

        InputExtension
        OutputExtension
        ToolExtension

    Is responsible for:

    * Identifying the extensions
    * Creating Tool, Input, & Output Menu ID References
    * Providing the callbacks that invoke the appropriate methods on the
    appropriate extensions to invoke their functionality.


    By convention prefix the plugin tool module name with the characters 'Tool'
    By convention prefix the plugin input module name with 'Input'
    By convention prefix the plugin output module name with 'Output'

    """
    def __init__(self):

        self.logger: Logger = getLogger(__name__)

        self._extensionPreferences: ExtensionPreferences = ExtensionPreferences()
        #
        #
        #
        self._inputExtensionsMap:  InputExtensionMap   = InputExtensionMap()

        self._inputExtensionClasses:  ExtensionList = cast(ExtensionList, None)

    @property
    def inputExtensions(self) -> ExtensionList:
        """
        Get the input extension types.  Lazy creation

        Returns:  A copy of the list of input extension classes
        """

        if self._inputExtensionClasses is None:
            self._inputExtensionClasses = ExtensionList([])
            for extension in INPUT_EXTENSIONS:
                extensionClass = cast(type, extension)
                classInstance = extensionClass(None)
                if classInstance.inputFormat is not None:
                    self._inputExtensionClasses.append(extension)

        return ExtensionList(self._inputExtensionClasses[:])

    @property
    def inputExtensionMap(self) -> InputExtensionMap:

        if len(self._inputExtensionsMap.extensionIdMap) == 0:
            self._inputExtensionsMap.extensionIdMap = self._mapWxIdsToExtensions(self.inputExtensions)

        return self._inputExtensionsMap

    def doImport(self, wxId: WindowId) -> ExtensionDetails:
        """
        Args:
            wxId:       The ID ref of the menu item
        """
        idMap:          ExtensionIDMap        = self.inputExtensionMap.extensionIdMap
        clazz:          type               = idMap[wxId]
        pluginInstance: BaseInputExtension = clazz(pluginAdapter=self._extensionPreferences)

        self._doExtensionAction(methodToCall=pluginInstance.executeImport)

        return ExtensionDetails(name=pluginInstance.name, version=pluginInstance.version, author=pluginInstance.author)

    def _doExtensionAction(self, methodToCall: Callable):
        """
        Args:
            methodToCall:
        """

        try:
            methodToCall()
        except (ValueError, Exception) as e:
            self.logger.error(f'{e}')
            booBoo: MessageDialog = MessageDialog(parent=None,
                                                  message=f'An error occurred while executing the selected extension - {e}',
                                                  caption='Error!', style=OK | ICON_ERROR)
            booBoo.ShowModal()

    def _mapWxIdsToExtensions(self, extensionList: ExtensionList) -> ExtensionIDMap:
        """

        Args:
            extensionList:   List of the extensions to map

        Returns:  A map of window IDs to their associated extension types
        """

        pluginMap: ExtensionIDMap = ExtensionIDMap({})

        nb: int = len(extensionList)

        for x in range(nb):
            wxId: WindowId = NewIdRef()

            pluginMap[wxId] = extensionList[x]

        return pluginMap
