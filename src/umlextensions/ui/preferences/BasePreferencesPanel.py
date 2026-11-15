
from abc import ABC
from abc import abstractmethod

from wx import BORDER_DEFAULT
from wx import Window

from wx.lib.sized_controls import SizedPanel

from umlextensions.Common import WxABCMeta
from umlextensions.ExtensionsPreferences import ExtensionsPreferences


class BasePreferencesPanel(SizedPanel, ABC, metaclass=WxABCMeta):
    """
    Abstract base class for all umlextensions preferences section panels.
    Subclasses must provide a name property (used as the notebook tab label)
    and implement _setControlValues to populate controls from preferences.
    """

    def __init__(self, parent: Window, style: int = BORDER_DEFAULT):

        super().__init__(parent, style=style)

        self._preferences: ExtensionsPreferences = ExtensionsPreferences()

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError('Subclasses must implement name')

    @abstractmethod
    def _setControlValues(self):
        raise NotImplementedError('Subclasses must implement _setControlValues')

    def _fixPanelSize(self, panel: SizedPanel):
        """
        A little trick to make sure that the sizer cannot be resized to
        less screen space than the controls need.

        Args:
            panel:
        """
        panel.Fit()
        panel.SetMinSize(panel.GetSize())
