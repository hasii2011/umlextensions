from pathlib import Path
from typing import Callable
from typing import cast

from logging import Logger
from logging import getLogger

from wx import EVT_MENU
from wx import FD_CHANGE_DIR
from wx import FD_OPEN
from wx import ID_EXIT
from wx import FD_FILE_MUST_EXIST
from wx import DEFAULT_FRAME_STYLE
from wx import FRAME_FLOAT_ON_PARENT
from wx import ID_PREFERENCES
from wx import ID_SELECTALL

from wx import Menu
from wx import Size
from wx import MenuBar
from wx import CommandEvent
from wx import FileSelector

from wx import NewIdRef as wxNewIdRef

from wx.lib.sized_controls import SizedFrame
from wx.lib.sized_controls import SizedPanel

from umlshapes.ShapeTypes import UmlShapes
from umlshapes.ShapeTypes import UmlLinkGenre
from umlshapes.ShapeTypes import UmlShapeGenre
from umlshapes.ShapeTypes import umlShapesFactory
from umlshapes.UmlDiagram import UmlDiagram

from umlshapes.shapes.UmlClass import UmlClass
from umlshapes.shapes.UmlNote import UmlNote

from umlshapes.links.UmlAggregation import UmlAggregation
from umlshapes.links.UmlAssociation import UmlAssociation
from umlshapes.links.UmlComposition import UmlComposition
from umlshapes.links.UmlInheritance import UmlInheritance
from umlshapes.links.UmlNoteLink import UmlNoteLink

from umlshapes.links.eventhandlers.UmlAssociationEventHandler import UmlAssociationEventHandler
from umlshapes.links.eventhandlers.UmlLinkEventHandler import UmlLinkEventHandler
from umlshapes.links.eventhandlers.UmlNoteLinkEventHandler import UmlNoteLinkEventHandler

from umlshapes.shapes.eventhandlers.UmlClassEventHandler import UmlClassEventHandler

from umlshapes.types.UmlPosition import UmlPosition

from umlshapes.frames.ClassDiagramFrame import ClassDiagramFrame

from umlshapes.pubsubengine.UmlPubSubEngine import UmlPubSubEngine

from umlshapes.UmlBaseEventHandler import UmlBaseEventHandler

from umlio.Reader import Reader
from umlio.IOTypes import UmlProject
from umlio.IOTypes import XML_SUFFIX
from umlio.IOTypes import UmlClasses
from umlio.IOTypes import UmlDocument
from umlio.IOTypes import UmlLinks

from umlextensions.ExtensionsManager import ToolExtensionMap
from umlextensions.ExtensionsTypes import FrameSize
from umlextensions.ExtensionsManager import WindowId
from umlextensions.ExtensionsManager import ExtensionDetails
from umlextensions.ExtensionsPubSub import ExtensionsPubSub
from umlextensions.ExtensionsTypes import FrameInformation
from umlextensions.ExtensionsManager import ExtensionsManager
from umlextensions.ExtensionsManager import InputExtensionMap
from umlextensions.ExtensionsPubSub import ExtensionsMessageType
from umlextensions.ExtensionsTypes import SelectedUmlShapesCallback

from umlextensions.input.BaseInputExtension import BaseInputExtension

FRAME_WIDTH:  int = 1024
FRAME_HEIGHT: int = 720

ID_LOAD_XML_FILE: int = wxNewIdRef()

XML_WILDCARD:     str = f'Extensible Markup Language (*.{XML_SUFFIX})|*{XML_SUFFIX}'


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
        pluginPubSub.subscribe(ExtensionsMessageType.WIGGLE_SHAPES, listener=self._wiggleShapesListener)

        pluginPubSub.subscribe(ExtensionsMessageType.GET_SELECTED_UML_SHAPES, listener=self._getSelectedUmlShapesListener)

    def _createApplicationMenuBar(self):

        menuBar:        MenuBar = MenuBar()
        fileMenu:       Menu = Menu()
        editMenu:       Menu = Menu()
        extensionsMenu: Menu = Menu()

        fileMenu.Append(ID_LOAD_XML_FILE, '&Load XML File', 'External Diagrammer File')
        fileMenu.AppendSeparator()
        fileMenu.Append(ID_EXIT, '&Quit', 'Quit Application')
        fileMenu.AppendSeparator()
        fileMenu.Append(ID_PREFERENCES, "P&references", 'UML preferences')

        editMenu.Append(ID_SELECTALL)

        inputSubMenu: Menu = self._makeInputSubMenu()
        toolsSubMenu: Menu = self._makeToolSubMenu()

        extensionsMenu.AppendSubMenu(inputSubMenu, 'Input')
        # extensionsMenu.AppendSubMenu(outputSubMenu, 'Output')
        extensionsMenu.AppendSubMenu(toolsSubMenu, 'Tools')

        menuBar.Append(fileMenu, 'File')
        menuBar.Append(editMenu, 'Edit')
        menuBar.Append(extensionsMenu, 'Extensions')

        self.Bind(EVT_MENU, self._onOpenXmlFile, id=ID_LOAD_XML_FILE)
        self.Bind(EVT_MENU, self._onSelectAll,   id=ID_SELECTALL)

        self.SetMenuBar(menuBar)

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

    def _makeToolSubMenu(self) -> Menu:
        subMenu: Menu = Menu()

        toolExtensionsMap: ToolExtensionMap = self._extensionManager.toolExtensionsMap

        for wxId in toolExtensionsMap.extensionIdMap.keys():
            clazz:        type = toolExtensionsMap.extensionIdMap[wxId]
            toolInstance: BaseInputExtension = clazz(None)

            toolName: str = toolInstance.name
            subMenu = self._makeSubMenuEntry(subMenu=subMenu, wxId=wxId, pluginName=toolName, callback=self._onToolAction)

        return subMenu

    def _onImport(self, event: CommandEvent):
        wxId:          int           = event.GetId()
        extensionsDetails: ExtensionDetails = self._extensionManager.doImport(wxId=cast(WindowId, wxId))
        self.logger.info(f'Import: {extensionsDetails=}')

    def _onToolAction(self, event: CommandEvent):
        wxId:          int           = event.GetId()
        extensionsDetails: ExtensionDetails = self._extensionManager.doToolAction(wxId=cast(WindowId, wxId))
        self.logger.info(f'Import: {extensionsDetails=}')

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
            selectedUmlShapes=self._getSelectedUmlShapes(),
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

    def _wiggleShapesListener(self):
        """
        This is a hack work around to simulate moving the shapes so
        that the links are visible.
        I tried refresh, redraw, and .DrawLinks;  None of it worked
        """

        umlShapes: UmlShapes = self._diagramFrame.umlShapes

        for shape in umlShapes:

            if isinstance(shape, UmlShapeGenre) is True:

                umlShape: UmlShapeGenre = cast(UmlShapeGenre, shape)

                oldPosition: UmlPosition = umlShape.position
                newPosition: UmlPosition = UmlPosition(x=oldPosition.x + 10, y=oldPosition.y + 10)

                eventHandler: UmlBaseEventHandler = umlShape.GetEventHandler()

                eventHandler.OnDragLeft(draw=True, x=newPosition.x, y=newPosition.y)
                eventHandler.OnDragLeft(draw=True, x=oldPosition.x, y=oldPosition.y)

    def _getSelectedUmlShapesListener(self, callback: SelectedUmlShapesCallback):
        selectedShapes: UmlShapes = self._getSelectedUmlShapes()
        callback(selectedShapes)

    def _getSelectedUmlShapes(self) -> UmlShapes:

        umlShapes:      UmlShapes = self._diagramFrame.umlShapes
        selectedShapes: UmlShapes  = umlShapesFactory()

        for s in umlShapes:
            if isinstance(s, UmlShapeGenre) or isinstance(s, UmlLinkGenre):
                umlShape: UmlShapeGenre | UmlLinkGenre = cast(UmlShapeGenre | UmlLinkGenre, s)

                if umlShape.selected is True:
                    selectedShapes.append(umlShape)

        return selectedShapes

    # noinspection PyUnusedLocal
    def _onOpenXmlFile(self, event: CommandEvent):

        selectedFile: str = FileSelector("Choose a XML file to load", wildcard=XML_WILDCARD, flags=FD_OPEN | FD_FILE_MUST_EXIST | FD_CHANGE_DIR)
        if selectedFile != '':
            reader: Reader = Reader()
            umlProject: UmlProject = reader.readXmlFile(fileName=Path(selectedFile))
            self.logger.debug(f'{umlProject=}')
            self._loadProject(umlProject)

    # noinspection PyUnusedLocal
    def _onSelectAll(self, event: CommandEvent):
        umlShapes: UmlShapes = self._diagramFrame.umlShapes

        for shape in umlShapes:
            if isinstance(shape, UmlShapeGenre) is True or isinstance(shape, UmlLinkGenre) is True:
                shape.selected = True
        self._diagramFrame.refresh()

    def _loadProject(self, umlProject: UmlProject):

        assert len(umlProject.umlDocuments) == 1, 'Currently we only handle single document projects'

        for umlDocumentTitle, umlDocument in umlProject.umlDocuments.items():
            self._layoutShapes(diagramFrame=self._diagramFrame, umlDocument=umlDocument)

    def _layoutShapes(self, diagramFrame: ClassDiagramFrame, umlDocument: UmlDocument):
        self._layoutClasses(diagramFrame, umlDocument.umlClasses)
        self._layoutLinks(diagramFrame, umlDocument.umlLinks)

    def _layoutClasses(self, diagramFrame: ClassDiagramFrame, umlClasses: UmlClasses):
        for umlClass in umlClasses:
            self._layoutShape(
                umlShape=umlClass,
                diagramFrame=diagramFrame,
                eventHandlerClass=UmlClassEventHandler
            )

    def _layoutLinks(self, diagramFrame: ClassDiagramFrame, umlLinks: UmlLinks):
        for umlLink in umlLinks:
            umlLink.umlFrame = diagramFrame
            if isinstance(umlLink, UmlInheritance):
                umInheritance: UmlInheritance = cast(UmlInheritance, umlLink)
                subClass  = umInheritance.subClass
                baseClass = umInheritance.baseClass

                subClass.addLink(umlLink=umInheritance, destinationClass=baseClass)

                diagramFrame.umlDiagram.AddShape(umInheritance)
                umInheritance.Show(True)

                umlLinkEventHandler: UmlLinkEventHandler = UmlLinkEventHandler(umlLink=umlLink)
                umlLinkEventHandler.umlPubSubEngine = self._umlPubSubEngine
                umlLinkEventHandler.SetPreviousHandler(umlLink.GetEventHandler())
                umlLink.SetEventHandler(umlLinkEventHandler)

            elif isinstance(umlLink, UmlNoteLink):
                umlNoteLink: UmlNoteLink = cast(UmlNoteLink, umlLink)
                sourceNote:       UmlNote  = umlNoteLink.sourceNote
                destinationClass: UmlClass = umlNoteLink.destinationClass

                sourceNote.addLink(umlNoteLink=umlNoteLink, umlClass=destinationClass)

                diagramFrame.umlDiagram.AddShape(umlNoteLink)
                umlNoteLink.Show(True)
                eventHandler: UmlNoteLinkEventHandler = UmlNoteLinkEventHandler(umlNoteLink=umlNoteLink)
                eventHandler.umlPubSubEngine = self._umlPubSubEngine
                eventHandler.SetPreviousHandler(umlLink.GetEventHandler())
                umlNoteLink.SetEventHandler(eventHandler)
            elif isinstance(umlLink, (UmlAssociation, UmlComposition, UmlAggregation)):

                source      = umlLink.sourceShape
                destination = umlLink.destinationShape
                source.addLink(umlLink, destination)  # type: ignore

                diagramFrame.umlDiagram.AddShape(umlLink)
                umlLink.Show(True)

                umlAssociationEventHandler: UmlAssociationEventHandler = UmlAssociationEventHandler(umlAssociation=umlLink)
                umlAssociationEventHandler.umlPubSubEngine = self._umlPubSubEngine
                umlAssociationEventHandler.SetPreviousHandler(umlLink.GetEventHandler())
                umlLink.SetEventHandler(umlAssociationEventHandler)

    def _layoutShape(self, umlShape: UmlShapeGenre, diagramFrame: ClassDiagramFrame, eventHandlerClass: type[UmlBaseEventHandler]):
        """

        Args:
            umlShape:
            diagramFrame:
            eventHandlerClass:
        """

        umlShape.umlFrame = diagramFrame
        diagram: UmlDiagram = diagramFrame.umlDiagram

        eventHandler: UmlBaseEventHandler = eventHandlerClass()
        eventHandler.SetShape(umlShape)
        eventHandler.umlPubSubEngine = self._umlPubSubEngine
        eventHandler.SetPreviousHandler(umlShape.GetEventHandler())
        umlShape.SetEventHandler(eventHandler)

        diagram.AddShape(umlShape)
        umlShape.Show(True)

        diagramFrame.refresh()
