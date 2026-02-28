
from typing import cast

from logging import Logger
from logging import getLogger

from wx.lib.sized_controls import SizedPanel

from umlshapes.dialogs.BaseEditDialog import BaseEditDialog

from codeallyadvanced.ui.widgets.DimensionsControl import DimensionsControl

from umlextensions.ExtensionsPreferences import ExtensionsPreferences
from umlextensions.tools.orthogonallayout.LayoutAreaDimensions import LayoutAreaDimensions


class DlgLayoutDimensions(BaseEditDialog):

    def __init__(self, parent):

        super().__init__(parent, title='Layout Size')

        self.logger:       Logger          = getLogger(__name__)

        self._preferences:  ExtensionsPreferences = ExtensionsPreferences()

        layoutAreaSize: LayoutAreaDimensions = self._preferences.orthogonalLayoutSize
        self._layoutWidth:  int = layoutAreaSize.width
        self._layoutHeight: int = layoutAreaSize.height

        self._layoutSizeControl: DimensionsControl = cast(DimensionsControl, None)

        self._layoutSizeControls(parent=self.GetContentsPane())
        self._layoutStandardOkCancelButtonSizer()
        self.Fit()
        self.SetMinSize(self.GetSize())

    @property
    def layoutWidth(self) -> int:
        return self._layoutWidth

    @property
    def layoutHeight(self) -> int:
        return self._layoutHeight

    def _layoutSizeControls(self, parent: SizedPanel):

        self._layoutSizeControl = DimensionsControl(sizedPanel=parent, displayText="Layout Width/Height",
                                                    minValue=480, maxValue=4096,
                                                    valueChangedCallback=self._onSizeChange,
                                                    setControlsSize=True)

        self._layoutSizeControl.dimensions = self._preferences.orthogonalLayoutSize

    def _onSizeChange(self, newValue: LayoutAreaDimensions):

        self._layoutWidth  = newValue.width
        self._layoutHeight = newValue.height

        self._preferences.orthogonalLayoutSize = newValue
