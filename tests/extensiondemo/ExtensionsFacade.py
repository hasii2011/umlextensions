
from typing import cast

from logging import Logger
from logging import getLogger

from umlshapes.ShapeTypes import UmlLinkGenre
from umlshapes.ShapeTypes import UmlShapeGenre

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

from umlextensions.ExtensionsTypes import FrameInformationCallback
from umlextensions.ExtensionsTypes import SelectedUmlShapesCallback

from umlextensions.IExtensionsFacade import IExtensionsFacade

from umlextensions.ExtensionsPubSub import ExtensionsMessageType


class ExtensionsFacade(IExtensionsFacade):
    """
    This class simplifies communication between the extensions
    and the UML Diagrammer

    This is a demonstration method that only works with this simple demonstration
    application
    """

    def __init__(self):

        super().__init__()
        self.logger: Logger = getLogger(__name__)

        self._umlPubSub: IUmlPubSubEngine = cast(IUmlPubSubEngine, None)

    @property
    def umlPubSub(self) -> IUmlPubSubEngine:
        return self._umlPubSub

    @umlPubSub.setter
    def umlPubSub(self, umlPubSub: IUmlPubSubEngine):
        self._umlPubSub = umlPubSub

    def requestCurrentFrameInformation(self, callback: FrameInformationCallback):
        self.extensionsPubSub.sendMessage(messageType=ExtensionsMessageType.REQUEST_FRAME_INFORMATION, callback=callback)

    def selectUmlShapes(self):
        self.extensionsPubSub.sendMessage(messageType=ExtensionsMessageType.SELECT_UML_SHAPES)

    def getSelectedUmlShapes(self, callback: SelectedUmlShapesCallback):
        self.extensionsPubSub.sendMessage(messageType=ExtensionsMessageType.GET_SELECTED_UML_SHAPES, callback=callback)

    def extensionModifiedProject(self):
        self.extensionsPubSub.sendMessage(messageType=ExtensionsMessageType.EXTENSION_MODIFIED_PROJECT)

    def refreshFrame(self):
        self.extensionsPubSub.sendMessage(messageType=ExtensionsMessageType.REFRESH_FRAME)

    def addShape(self, umlShape: UmlShapeGenre | UmlLinkGenre):
        self.extensionsPubSub.sendMessage(messageType=ExtensionsMessageType.ADD_SHAPE, umlShape=umlShape)

    def wiggleShapes(self):
        self.extensionsPubSub.sendMessage(messageType=ExtensionsMessageType.WIGGLE_SHAPES)
