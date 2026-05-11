
from typing import cast
from typing import NewType

from pathlib import Path

from wx import ART_TIP
from wx import ArtProvider
from wx import BITMAP_TYPE_PNG

from wx import FONTSTYLE_ITALIC
from wx import FONTSTYLE_NORMAL
from wx import FONTWEIGHT_BOLD
from wx import FONTWEIGHT_NORMAL

from wx import Font
from wx import FontStyle
from wx import Image
from wx import Bitmap
from wx import Window
from wx import ClientDC
from wx import MemoryDC
from wx import NullBitmap
from wx import BitmapType

from wx.lib.agw.balloontip import BT_LEAVE
from wx.lib.agw.balloontip import BT_ROUNDED
from wx.lib.agw.balloontip import BalloonTip

from umlshapes.types.UmlColor import UmlColor
from umlshapes.types.UmlFontFamily import UmlFontFamily
from umlshapes.utils.ResourceUtils import ResourceUtils

from umlextensions.ExtensionsPreferences import ExtensionsPreferences
from umlextensions.ExtensionsTypes import FrameInformation

NO_PARENT_WINDOW: Window = cast(Window, cast(object, None))

# Return type from wx.NewIdRef()
WindowId = NewType('WindowId', int)


def createScreenImageFile(frameInformation: FrameInformation, imagePath: Path, imageType: BitmapType = BITMAP_TYPE_PNG) -> bool:
    """
    Create a screen image file
    Args:
        frameInformation:   Plugin frame information
        imagePath:          Where to write the image file to
        imageType:          Defaults to png

    Returns: 'True' for a successful creation else 'False'

    """

    context:   ClientDC   = frameInformation.clientDC
    memory:    MemoryDC   = MemoryDC()

    x: int = frameInformation.frameSize.width
    y: int = frameInformation.frameSize.height
    emptyBitmap: Bitmap = Bitmap(x, y, -1)

    memory.SelectObject(emptyBitmap)
    memory.Blit(source=context, xsrc=0, height=y, xdest=0, ydest=0, ysrc=0, width=x)
    memory.SelectObject(NullBitmap)

    img: Image = emptyBitmap.ConvertToImage()

    status: bool = img.SaveFile(str(imagePath), imageType)

    return status

def createBalloonTip(tipTitle: str, tipText: str, tipTarget: Window):
    """
    TODO:  Should we be using UML Shape facilities

    Args:
        tipTitle:   The tip title
        tipText:    The tip text
        tipTarget:  The tip target

    Returns:    A standard balloon tool tip
    """

    def getFont(size: int, familyStr: UmlFontFamily, bold: bool, italic: bool) -> Font:
        """

        Args:
            size:       The font size
            familyStr:  The string that needs to be converted to the appropriate wx font family
            bold:       Indicates if the font should be bold
            italic:     Indicates if teh font should be italicized

        Returns:   The appropriate font
        """
        fontFamily: int      = ResourceUtils.umlFontFamilyToWxFontFamily(familyStr)
        fontWeight: int      = FONTWEIGHT_BOLD if bold else FONTWEIGHT_NORMAL
        fontStyle: FontStyle = FONTSTYLE_ITALIC if italic else FONTSTYLE_NORMAL

        return Font(size, fontFamily, fontStyle, fontWeight)

    preferences: ExtensionsPreferences = ExtensionsPreferences()

    balloonTip: BalloonTip = BalloonTip(topicon=ArtProvider.GetBitmap(ART_TIP),
                                        toptitle=tipTitle,
                                        message=tipText,
                                        shape=BT_ROUNDED,
                                        tipstyle=BT_LEAVE)

    balloonTip.SetTitleFont(getFont(
        preferences.balloonTipTitleFontSize,
        preferences.balloonTipTitleFontFamily,
        preferences.balloonTipTitleBold,
        preferences.balloonTipTitleItalicize
    ))
    balloonTip.SetTitleColour(UmlColor.toWxColor(preferences.balloonTipTitleColor))

    balloonTip.SetMessageFont(getFont(
        preferences.balloonTipTextFontSize,
        preferences.balloonTipTextFontFamily,
        preferences.balloonTipTextBold,
        preferences.balloonTipTextItalicize
    ))
    balloonTip.SetMessageColour(UmlColor.toWxColor(preferences.balloonTipTextColor))

    balloonTip.SetBalloonColour(UmlColor.toWxColor(preferences.balloonColor))
    balloonTip.SetTarget(tipTarget)
