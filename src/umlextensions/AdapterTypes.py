#
#  These types are visible to the extension adapter the
#  implementor of the adapter
#
from typing import cast
from typing import Callable

from dataclasses import dataclass
from dataclasses import field

from wx import ClientDC

from umlshapes.ShapeTypes import UmlShapes
from umlshapes.ShapeTypes import umlShapesFactory


@dataclass
class FrameSize:
    """
    The strategy is to provide minimal information to the pyutplugins
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
    frameActive:        bool       = False
    selectedOglObjects: UmlShapes = field(default_factory=umlShapesFactory)
    diagramTitle:       str         = ''
    diagramType:        str        = ''
    frameSize:          FrameSize  = field(default_factory=createFrameSizeFactory)
    clientDC:           ClientDC   = cast(ClientDC, None)


FrameInformationCallback = Callable[[FrameInformation], None]
FrameSizeCallback        = Callable[[FrameSize], None]

NO_INTEGER: int = cast(int, None)
