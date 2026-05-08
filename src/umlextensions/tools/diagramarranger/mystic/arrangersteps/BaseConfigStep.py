
from abc import ABC
from abc import ABCMeta
from abc import abstractmethod

from wx.lib.sized_controls import SizedPanel

from codeallyadvanced.ui.mystic.MysticStepBase import MysticStepBase

from umlextensions.ExtensionsPreferences import ExtensionsPreferences

from umlextensions.tools.diagramarranger.ArrangerType import ArrangerType


class MetaMysticPageBase(ABCMeta, type(MysticStepBase)):        # type: ignore
    """
    I have no idea why this works:
    https://stackoverflow.com/questions/66591752/metaclass-conflict-when-trying-to-create-a-python-abstract-class-that-also-subcl
    """


class BaseConfigStep(MysticStepBase, ABC, metaclass=MetaMysticPageBase):

    def __init__(self, parent: SizedPanel, configuresArranger: ArrangerType ):

        super().__init__(parent=parent)

        self._configuresArranger: ArrangerType          = configuresArranger
        self._preferences:        ExtensionsPreferences = ExtensionsPreferences()

        self.SetSizerType('vertical')
        self.SetSizerProps(expand=True, proportion=1)     # noqa

        self._createPageTitle()

    @property
    def configuresArranger(self) -> ArrangerType:
        return self._configuresArranger

    @abstractmethod
    def _createPageTitle(self):
        pass
