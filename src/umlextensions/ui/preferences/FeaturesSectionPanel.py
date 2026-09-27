
from typing import cast

from logging import Logger
from logging import getLogger

from pathlib import Path

from wx import EVT_CHECKBOX
from wx import ID_ANY

from wx import CheckBox
from wx import CommandEvent
from wx import Window
from wx import Size

from wx.lib.sized_controls import SizedStaticBox

from codeallyadvanced.ui.widgets.DirectorySelector import DirectorySelector
from codeallyadvanced.ui.widgets.DirectorySelector import DirectorySelectorParameters

from umlextensions.ExtensionsPreferences import ExtensionsPreferences
from umlextensions.ui.preferences.BaseExtPreferencesPanel import BaseExtPreferencesPanel


class FeaturesSectionPanel(BaseExtPreferencesPanel):
    """
    Preferences panel for the 'Features' INI section.

    Covers:
        startDirectory           - DirectorySelector
        diagnoseOrthogonalRouter - CheckBox
    """

    PANEL_NAME: str = 'Features'

    def __init__(self, parent: Window):

        super().__init__(parent)

        self.logger: Logger = getLogger(__name__)

        self.SetSizerType('vertical')

        self._directorySelector:       DirectorySelector = cast(DirectorySelector, None)    # noqa
        self._diagnoseOrthogonalRouter: CheckBox         = cast(CheckBox, None)             # noqa

        self._layoutControls()
        self._setControlValues()

    @property
    def name(self) -> str:
        return FeaturesSectionPanel.PANEL_NAME

    def _layoutControls(self):
        """
        Builds and lays out the preference controls for the features section.
        """
        self._layoutStartDirectory()
        self._layoutDiagnostics()

    def _layoutStartDirectory(self):
        """
        Lays out the start directory selection control.
        """
        dirParams: DirectorySelectorParameters = DirectorySelectorParameters(
            caption='Start Directory',
            pathChangedCallback=self._onStartDirectoryChanged,
        )
        self._directorySelector = DirectorySelector(parent=self, parameters=dirParams)
        self._directorySelector.SetSizerProps(expand=True)

    def _layoutDiagnostics(self):
        """
        Lays out the diagnostics checkbox box.
        """
        diagnosticsBox: SizedStaticBox = SizedStaticBox(self, ID_ANY, 'Diagnostics')
        diagnosticsBox.SetSizerType('vertical')
        diagnosticsBox.SetMinSize(Size(-1, 60))
        diagnosticsBox.SetSizerProps(expand=True)

        self._diagnoseOrthogonalRouter = CheckBox(diagnosticsBox, ID_ANY, 'Diagnose Orthogonal Router')
        self._diagnoseOrthogonalRouter.SetToolTip('Enable verbose diagnostics for the orthogonal routing algorithm')
        self.Bind(EVT_CHECKBOX, self._onDiagnoseOrthogonalRouterChanged, self._diagnoseOrthogonalRouter)

    def _setControlValues(self):

        p: ExtensionsPreferences = self._preferences

        startDir: str = p.startDirectory
        if startDir:
            self._directorySelector.directoryPath = Path(startDir)

        self._diagnoseOrthogonalRouter.SetValue(p.diagnoseOrthogonalRouter)

    # ── Event Handlers ───────────────────────────────────────────────────────

    def _onStartDirectoryChanged(self, newPath: Path):
        self._preferences.startDirectory = str(newPath)

    def _onDiagnoseOrthogonalRouterChanged(self, event: CommandEvent):
        self._preferences.diagnoseOrthogonalRouter = event.IsChecked()
