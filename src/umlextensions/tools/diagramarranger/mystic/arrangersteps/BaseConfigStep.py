
from typing import Callable

from abc import ABC
from abc import ABCMeta
from abc import abstractmethod

from wx.lib.sized_controls import SizedPanel

from wx import EVT_BUTTON

from wx import Button
from wx import NewIdRef
from wx import CommandEvent

from codeallyadvanced.ui.mystic.MysticStepBase import MysticStepBase

from umlextensions.Common import WindowId
from umlextensions.ExtensionsPreferences import ExtensionsPreferences

from umlextensions.tools.diagramarranger.ArrangerType import ArrangerType

LayoutCallback   = Callable[[ArrangerType], None]
UndoCallback     = Callable[[], None]

class MetaMysticPageBase(ABCMeta, type(MysticStepBase)):        # type: ignore
    """
    I have no idea why this works:
    https://stackoverflow.com/questions/66591752/metaclass-conflict-when-trying-to-create-a-python-abstract-class-that-also-subcl
    """
ID_UNDO:   WindowId = NewIdRef()
ID_LAYOUT: WindowId = NewIdRef()


class BaseConfigStep(MysticStepBase, ABC, metaclass=MetaMysticPageBase):
    """
    The subclasses implement the abstract methods to get a standard looking
    configuration and run step
    """

    def __init__(self, parent: SizedPanel, configuresArranger: ArrangerType, layoutCallback: LayoutCallback, undoCallback: UndoCallback):
        """

        Args:
            parent:   The parent sized panel
            configuresArranger:     They type of arranger configuration we configure
            layoutCallback:         Method to call to re-arrange UML Diagram
            undoCallback:           Method to call to undo last arrangement
        """

        super().__init__(parent=parent)

        self._configuresArranger: ArrangerType   = configuresArranger
        self._layoutCallback:     LayoutCallback = layoutCallback
        self._undoCallback:       UndoCallback   = undoCallback

        self._preferences: ExtensionsPreferences = ExtensionsPreferences()

        self.SetSizerType('vertical')
        self.SetSizerProps(expand=True, proportion=1)   # noqa

        self._layoutPageTitle()
        self._layoutConfigPanel()
        self._layoutButtonPanel(self)

    @property
    def configuresArranger(self) -> ArrangerType:
        return self._configuresArranger

    def _layoutButtonPanel(self, parent: SizedPanel):

        buttonPanel: SizedPanel = SizedPanel(parent)
        buttonPanel.SetSizerType('horizontal')
        buttonPanel.SetSizerProps(expand=False, halign='right')  # expand False allows aligning right
        #
        # Layout custom buttons here
        #
        self._btnUndo   = Button(buttonPanel, ID_UNDO,   label='Undo')
        self._btnLayout = Button(buttonPanel, ID_LAYOUT, label='Layout')

        self.Bind(EVT_BUTTON, self._onUndo,   self._btnUndo)
        self.Bind(EVT_BUTTON, self._onLayout, self._btnLayout)
        #
        self._btnLayout.SetDefault()

    @abstractmethod
    def _layoutPageTitle(self):
        pass

    @abstractmethod
    def _layoutConfigPanel(self):
        pass

    # noinspection PyUnusedLocal
    def _onUndo(self, event: CommandEvent):
        self._undoCallback()

    # noinspection PyUnusedLocal
    def _onLayout(self, event: CommandEvent):
        self._layoutCallback(self._configuresArranger)
