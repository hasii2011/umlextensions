
from typing import Callable
from typing import cast

from logging import Logger
from logging import getLogger

from wx import EVT_MENU
from wx import ID_EXIT
from wx import DEFAULT_FRAME_STYLE
from wx import FRAME_FLOAT_ON_PARENT
from wx import ID_PREFERENCES

from wx import Menu
from wx import Size
from wx import MenuBar
from wx import CommandEvent

from wx.lib.sized_controls import SizedFrame
from wx.lib.sized_controls import SizedPanel

from umlshapes.ShapeTypes import UmlShapes
from umlshapes.ShapeTypes import UmlLinkGenre
from umlshapes.ShapeTypes import UmlShapeGenre

from umlshapes.frames.ClassDiagramFrame import ClassDiagramFrame

from umlshapes.pubsubengine.UmlPubSubEngine import UmlPubSubEngine

from umlextensions.ExtensionsTypes import FrameSize
from umlextensions.ExtensionsManager import WindowId
from umlextensions.ExtensionsManager import ExtensionDetails
from umlextensions.ExtensionsPubSub import ExtensionsPubSub
from umlextensions.ExtensionsTypes import FrameInformation
from umlextensions.ExtensionsManager import ExtensionsManager
from umlextensions.ExtensionsManager import InputExtensionMap
from umlextensions.ExtensionsPubSub import ExtensionsMessageType

from umlextensions.input.BaseInputExtension import BaseInputExtension

FRAME_WIDTH:  int = 1024
FRAME_HEIGHT: int = 720


class ExtensionFrame(SizedFrame):
    def __init__(self):
        self.logger: Logger = getLogger(__name__)
        super().__init__(parent=None, title='Demo UML Extensions', size=(FRAME_WIDTH, FRAME_HEIGHT), style=DEFAULT_FRAME_STYLE | FRAME_FLOAT_ON_PARENT)

        sizedPanel: SizedPanel = self.GetContentsPane()
        sizedPanel.SetSizerProps(expand=True, proportion=1)

        self._umlPubSubEngine:  UmlPubSubEngine  = UmlPubSubEngine()
        self._editMenu:         Menu             = cast(Menu, None)
        self._extensionManager: ExtensionsManager = ExtensionsManager(umlPubSubEngine=self._umlPubSubEngine)

        self._createApplicationMenuBar()

        self._diagramFrame = ClassDiagramFrame(
            parent=sizedPanel,
            umlPubSubEngine=self._umlPubSubEngine,
        )
        # noinspection PyUnresolvedReferences
        self._diagramFrame.SetSizerProps(expand=True, proportion=1)
        pluginPubSub: ExtensionsPubSub = self._extensionManager.extensionsPubSub
        #
        # Putting the pub sub logic here is just a convenience
        #
        pluginPubSub.subscribe(ExtensionsMessageType.REQUEST_FRAME_INFORMATION,  listener=self._requestFrameInformationListener)
        pluginPubSub.subscribe(ExtensionsMessageType.EXTENSION_MODIFIED_PROJECT, listener=self._extensionModifiedListener)

        pluginPubSub.subscribe(ExtensionsMessageType.REFRESH_FRAME, listener=self._refreshFrameListener)
        pluginPubSub.subscribe(ExtensionsMessageType.ADD_SHAPE,     listener=self._addShapeListener)

    def _createApplicationMenuBar(self):

        menuBar:        MenuBar = MenuBar()
        fileMenu:       Menu = Menu()
        editMenu:       Menu = Menu()
        extensionsMenu: Menu = Menu()

        fileMenu.AppendSeparator()
        fileMenu.Append(ID_EXIT, '&Quit', "Quit Application")
        fileMenu.AppendSeparator()
        fileMenu.Append(ID_PREFERENCES, "P&references", "Uml preferences")

        inputSubMenu: Menu = self._makeInputSubMenu()
        extensionsMenu.AppendSubMenu(inputSubMenu, 'Input')
        # extensionsMenu.AppendSubMenu(outputSubMenu, 'Output')
        # extensionsMenu.AppendSubMenu(toolsSubMenu, 'Tools')

        menuBar.Append(fileMenu, 'File')
        menuBar.Append(editMenu, 'Edit')
        menuBar.Append(extensionsMenu, 'Extensions')

        self.SetMenuBar(menuBar)

    # def _makeToolsMenu(self, toolsMenu: Menu) -> Menu:
    #     """
    #     Make the Tools submenu.
    #     """
    #     idMap: PluginIDMap = self._pluginManager.toolPluginsMap.pluginIdMap
    #
    #     for wxId in idMap:
    #
    #         clazz: type = idMap[wxId]
    #
    #         pluginInstance: ToolPluginInterface = clazz(None)
    #         toolsMenu.Append(wxId, pluginInstance.menuTitle)
    #
    #         self.Bind(EVT_MENU, self._onTools, id=wxId)
    #
    #     return toolsMenu

    def _makeInputSubMenu(self) -> Menu:
        """
        Returns: The import submenu.
        """
        subMenu: Menu = Menu()

        inputExtensionsMap: InputExtensionMap = self._extensionManager.inputExtensionsMap

        for wxId in inputExtensionsMap.extensionIdMap.keys():
            clazz:          type = inputExtensionsMap.extensionIdMap[wxId]
            extensionInstance: BaseInputExtension = clazz(None)

            pluginName: str = extensionInstance.inputFormat.formatName

            subMenu = self._makeSubMenuEntry(subMenu=subMenu, wxId=wxId, pluginName=pluginName, callback=self._onImport)

        return subMenu

    def _onImport(self, event: CommandEvent):
        wxId:          int           = event.GetId()
        pluginDetails: ExtensionDetails = self._extensionManager.doImport(wxId=cast(WindowId, wxId))
        self.logger.info(f'Import: {pluginDetails=}')

    def _makeSubMenuEntry(self, subMenu: Menu, wxId: int, pluginName: str, callback: Callable) -> Menu:
        subMenu.Append(wxId, pluginName)
        self.Bind(EVT_MENU, callback, id=wxId)

        return subMenu

    # def _makeOutputSubMenu(self) -> Menu:
    #     """
    #     Returns:  The export submenu
    #     """
    #     pluginMap: OutputPluginMap = self._pluginManager.outputPluginsMap
    #
    #     return self._makeIOSubMenu(pluginMap=pluginMap)
    def _requestFrameInformationListener(self, callback: Callable):
        size: Size = self.GetSize()
        frameInfo: FrameInformation = FrameInformation(
            umlFrame=self._diagramFrame,
            frameActive=True,
            selectedOglObjects=UmlShapes([]),
            diagramTitle='Demo Class Diagram',
            diagramType='Class Document',
            frameSize=FrameSize(width=size.width, height=size.height)
        )
        callback(frameInfo)

    def _refreshFrameListener(self):
        self._diagramFrame.refresh()

    def _extensionModifiedListener(self):
        self.logger.info('********** Frame Modified ***********')

    def _addShapeListener(self, umlShape: UmlShapeGenre | UmlLinkGenre):
        self._diagramFrame.umlDiagram.AddShape(umlShape)
        umlShape.Show(True)
