
from abc import ABC
from abc import ABCMeta
from abc import abstractmethod

from wx import BORDER_DEFAULT
from wx import Window

from wx.lib.sized_controls import SizedPanel

from umlextensions.ExtensionsPreferences import ExtensionsPreferences


class _MyMetaBaseExtPreferencesPanel(ABCMeta, type(SizedPanel)):    # type: ignore
    """
    Resolves the metaclass conflict between ABCMeta and the wxPython SizedPanel metaclass.
    https://stackoverflow.com/questions/66591752/metaclass-conflict-when-trying-to-create-a-python-abstract-class-that-also-subcl
    """
    pass


class BaseExtPreferencesPanel(SizedPanel, ABC, metaclass=_MyMetaBaseExtPreferencesPanel):
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
        pass

    @abstractmethod
    def _setControlValues(self):
        pass

    def _fixPanelSize(self, panel: SizedPanel):
        """
        A little trick to make sure that the sizer cannot be resized to
        less screen space than the controls need.

        Args:
            panel:
        """
        panel.Fit()
        panel.SetMinSize(panel.GetSize())
