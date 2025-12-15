
from abc import ABC
from abc import abstractmethod

from umlshapes.ShapeTypes import UmlLinkGenre
from umlshapes.ShapeTypes import UmlShapeGenre

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

from umlextensions.ExtensionsPubSub import ExtensionsPubSub

from umlextensions.ExtensionsTypes import CreatedLinkCallback
from umlextensions.ExtensionsTypes import FrameInformation
from umlextensions.ExtensionsTypes import FrameInformationCallback
from umlextensions.ExtensionsTypes import IntegerList
from umlextensions.ExtensionsTypes import LinkInformation
from umlextensions.ExtensionsTypes import ObjectBoundaryCallback
from umlextensions.ExtensionsTypes import Points
from umlextensions.ExtensionsTypes import Rectangle
from umlextensions.ExtensionsTypes import Rectangles
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

    @abstractmethod
    def getShapeBoundaries(self, callback: ObjectBoundaryCallback):
        """
        Request the boundaries around all the UML objects
        on the current frame

        Args:
            callback:  The callback that receives the boundaries
        """
        pass

    @abstractmethod
    def deleteLink(self, umlLink: UmlLinkGenre):
        pass

    @abstractmethod
    def createLink(self, linkInformation: LinkInformation, callback: CreatedLinkCallback):
        pass

    @abstractmethod
    def showOrthogonalRoutingPoints(self, show: bool, spots: Points):
        pass

    @abstractmethod
    def showRulers(self, show: bool, horizontalRulers: IntegerList, verticalRulers: IntegerList, diagramBounds: Rectangle):
        pass

    @abstractmethod
    def showRouteGrid(self, show: bool, routeGrid: Rectangles):
        pass
