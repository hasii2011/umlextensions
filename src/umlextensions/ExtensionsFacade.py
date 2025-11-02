
from logging import Logger
from logging import getLogger

from umlextensions.ExtensionsTypes import FrameInformationCallback

from umlextensions.IExtensionsFacade import IExtensionsFacade

from umlextensions.ExtensionsPubSub import ExtensionsMessageType
from umlextensions.ExtensionsPubSub import ExtensionsPubSub


class ExtensionsFacade(IExtensionsFacade):
    """

    """

    def __init__(self, pubSub: ExtensionsPubSub):

        self.logger:  Logger           = getLogger(__name__)

        self._pubsub: ExtensionsPubSub = pubSub

    def requestCurrentFrameInformation(self, callback: FrameInformationCallback):
        self._pubsub.sendMessage(messageType=ExtensionsMessageType.REQUEST_FRAME_INFORMATION, callback=callback)

    def extensionModifiedProject(self):
        self._pubsub.sendMessage(messageType=ExtensionsMessageType.EXTENSION_MODIFIED_PROJECT)

    def refreshFrame(self):
        self._pubsub.sendMessage(messageType=ExtensionsMessageType.REQUEST_FRAME_INFORMATION)
