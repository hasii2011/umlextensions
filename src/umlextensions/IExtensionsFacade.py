
from abc import ABC
from abc import abstractmethod

from umlshapes.ShapeTypes import UmlLinkGenre
from umlshapes.ShapeTypes import UmlShapeGenre

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

from umlextensions.ExtensionsPubSub import ExtensionsPubSub
from umlextensions.ExtensionsTypes import FrameInformation
from umlextensions.ExtensionsTypes import FrameInformationCallback
from umlextensions.ExtensionsTypes import SelectedUmlShapesCallback


class IExtensionsFacade(ABC):
    """
    This facade simplifies communication to the UML diagrammer.  This interface serves as a front-facing interface
    that masks the complexity of the UML Diagrammer
    """
    def __init__(self):
        self._extensionsPubSub: ExtensionsPubSub = ExtensionsPubSub()

    @property
    def extensionsPubSub(self) -> ExtensionsPubSub:
        return self._extensionsPubSub

    @property
    @abstractmethod
    def umlPubSub(self) -> IUmlPubSubEngine:
        pass

    @umlPubSub.setter
    @abstractmethod
    def umlPubSub(self, umlPubSub: IUmlPubSubEngine):
        pass

    @abstractmethod
    def requestCurrentFrameInformation(self, callback: FrameInformationCallback) -> FrameInformation:
        pass

    @abstractmethod
    def extensionModifiedProject(self):
        pass

    @abstractmethod
    def selectUmlShapes(self):
        pass

    @abstractmethod
    def getSelectedUmlShapes(self, callback: SelectedUmlShapesCallback):
        pass

    @abstractmethod
    def refreshFrame(self):
        pass

    @abstractmethod
    def addShape(self, umlShape: UmlShapeGenre | UmlLinkGenre):
        pass

    @abstractmethod
    def wiggleShapes(self):
        pass
