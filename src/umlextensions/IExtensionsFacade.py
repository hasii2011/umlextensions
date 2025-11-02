
from abc import ABC
from abc import abstractmethod

from umlextensions.ExtensionsTypes import FrameInformation
from umlextensions.ExtensionsTypes import FrameInformationCallback


class IExtensionsFacade(ABC):
    """
    This facade simplifies communication to the UML diagrammer.  This interface serves as a front-facing interface
    that masks the complexity of the UML Diagrammer
    """
    @abstractmethod
    def requestCurrentFrameInformation(self, callback: FrameInformationCallback) -> FrameInformation:
        pass

    @abstractmethod
    def extensionModifiedProject(self):
        pass

    @abstractmethod
    def refreshFrame(self):
        pass
