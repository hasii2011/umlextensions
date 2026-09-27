
from typing import cast

from logging import Logger
from logging import getLogger

from wx.lib.sized_controls import SizedPanel

from umlshapes.dialogs.BaseEditDialog import BaseEditDialog

from codeallyadvanced.ui.widgets.DimensionsControl import DimensionsControl
from codeallyadvanced.ui.widgets.DimensionsControl import DimensionsParameters

from codeallybasic.Dimensions import Dimensions
from umlextensions.ExtensionsPreferences import ExtensionsPreferences


class DlgLayoutDimensions(BaseEditDialog):

    def __init__(self, parent):

        super().__init__(parent, title='Layout Size')

        self.logger:       Logger          = getLogger(__name__)

        self._preferences:  ExtensionsPreferences = ExtensionsPreferences()

        layoutAreaSize: Dimensions = self._preferences.orthogonalLayoutSize
        self._layoutWidth:  int = layoutAreaSize.width
        self._layoutHeight: int = layoutAreaSize.height

        self._layoutSizeControl: DimensionsControl = cast(DimensionsControl, None)  # noqa

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

        dimensionsParameters: DimensionsParameters = DimensionsParameters(
            caption='Layout Width/Height',
            minValue=480,
            maxValue=4096,
            valueChangedCallback=self._onSizeChange,
        )
        self._layoutSizeControl = DimensionsControl(parent=parent, parameters=dimensionsParameters)

        self._layoutSizeControl.dimensions = self._preferences.orthogonalLayoutSize

    def _onSizeChange(self, newValue: Dimensions):

        self._layoutWidth  = newValue.width
        self._layoutHeight = newValue.height

        self._preferences.orthogonalLayoutSize = newValue
