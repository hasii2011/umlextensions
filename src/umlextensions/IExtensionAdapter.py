
from abc import ABC
from abc import abstractmethod

from umlextensions.AdapterTypes import FrameInformationCallback


class IExtensionAdapter(ABC):
    """
    A diagramming system implements this interface in order to
    provide interfaces to the plugins
    """
    def __init__(self):
        pass

    @abstractmethod
    def getFrameInformation(self, callback: FrameInformationCallback):
        pass
