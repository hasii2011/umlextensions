
from typing import cast

from logging import Logger
from logging import getLogger

from enum import Enum

from codeallybasic.UnitTestBase import UnitTestBase
from wx import App
from wx import CB_READONLY
from wx import ComboBox
from wx import CommandEvent
from wx import DEFAULT_FRAME_STYLE
from wx import EVT_COMBOBOX
from wx import FRAME_FLOAT_ON_PARENT
from wx import ID_ANY
from wx import OK

from wx.lib.sized_controls import SizedFrame
from wx.lib.sized_controls import SizedPanel
from wx.lib.sized_controls import SizedStaticBox

from umlextensions.ExtensionsPreferences import ExtensionsPreferences
from umlextensions.input.python.DlgShapeLayoutParameters import DlgShapeLayoutParameters


class DialogNamesEnum(Enum):

    DLG_SHAPE_LAYOUT_PARAMETERS = 'DlgShapeLayoutParameters'


class AppTestDialogs(App):

    NOTHING_SELECTED: int = -1

    def __init__(self, redirect: bool):

        UnitTestBase.setUpLogging()

        self.logger:        Logger            = getLogger(__name__)
        self._preferences:  ExtensionsPreferences = ExtensionsPreferences()

        self._frame:       SizedFrame        = cast(SizedFrame, None)

        super().__init__(redirect)

    def OnInit(self):

        UnitTestBase.setUpLogging()

        self._frame = SizedFrame(parent=None, id=ID_ANY, title="Test Plugin Dialogs", size=(600, 300), style=DEFAULT_FRAME_STYLE | FRAME_FLOAT_ON_PARENT)

        self._frame.Show(False)
        self.SetTopWindow(self._frame)

        self._layoutSelectionControls(self._frame)
        self._frame.Show(True)

        # a little trick to make sure that you can't resize the dialog to
        # less screen space than the controls need
        self._frame.Fit()
        self._frame.SetMinSize(self._frame.GetSize())

        return True

    def _layoutSelectionControls(self, parentFrame: SizedFrame):

        sizedPanel: SizedPanel = parentFrame.GetContentsPane()
        sizedPanel.SetSizerType('vertical')
        sizedPanel.SetSizerProps(expand=True, proportion=1)

        dialogChoices = []
        for dlgName in DialogNamesEnum:
            dialogChoices.append(dlgName.value)

        box: SizedStaticBox = SizedStaticBox(sizedPanel, ID_ANY, "Select Dialog to Test")
        box.SetSizerProps(expand=True, proportion=1)

        self._cmbDlgName: ComboBox = ComboBox(box, choices=dialogChoices, style=CB_READONLY)

        self._cmbDlgName.SetSelection(AppTestDialogs.NOTHING_SELECTED)

        parentFrame.Bind(EVT_COMBOBOX, self._onDlgNameSelectionChanged, self._cmbDlgName)

    def _onDlgNameSelectionChanged(self, event: CommandEvent):

        dialogName: str = event.GetString()

        dlgNamesEnum: DialogNamesEnum = DialogNamesEnum(dialogName)

        self.logger.warning(f'Selected dialog: {dlgNamesEnum}')

        match dlgNamesEnum:
            case DialogNamesEnum.DLG_SHAPE_LAYOUT_PARAMETERS:
                with DlgShapeLayoutParameters(parent=self._frame) as dlg:
                    if dlg.ShowModal() == OK:
                        self.logger.info('Ok')


if __name__ == "__main__":

    testApp: AppTestDialogs = AppTestDialogs(redirect=False)

    testApp.MainLoop()
