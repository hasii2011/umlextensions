#
#  These types are visible to the extension adapter and the
#  implementor of the adapter
#
from typing import cast
from typing import Callable

from dataclasses import dataclass
from dataclasses import field

from wx import ClientDC

from umlshapes.frames.UmlFrame import UmlFrame

from umlshapes.ShapeTypes import UmlShapes
from umlshapes.ShapeTypes import umlShapesFactory

from umlio.IOTypes import UmlDocumentType


@dataclass
class FrameSize:
    """
    The strategy is to provide minimal information to the extensions
    we do not want them to not abuse it.
    """
    width:  int = -1
    height: int = -1


def createFrameSizeFactory() -> FrameSize:
    """
    Factory method to create  the OglClasses data structure;

    Returns:  A new data structure
    """
    return FrameSize()


@dataclass
class FrameInformation:
    """
    The document title is the name of the frame
    """
    umlFrame:           UmlFrame   = cast(UmlFrame, None)
    frameActive:        bool       = False
    selectedUmlShapes:  UmlShapes  = field(default_factory=umlShapesFactory)
    frameSize:          FrameSize  = field(default_factory=createFrameSizeFactory)
    clientDC:           ClientDC   = cast(ClientDC, None)
    diagramTitle:       str        = ''
    diagramType:        UmlDocumentType = UmlDocumentType.NOT_SET


FrameInformationCallback  = Callable[[FrameInformation], None]
FrameSizeCallback         = Callable[[FrameSize], None]
SelectedUmlShapesCallback = Callable[[UmlShapes], None]

NO_INTEGER: int = cast(int, None)
