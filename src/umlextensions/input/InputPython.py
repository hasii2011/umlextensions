
from typing import cast

from logging import Logger
from logging import getLogger

from wx import ICON_ERROR
from wx import MessageBox
from wx import OK
from wx import PD_APP_MODAL
from wx import PD_ELAPSED_TIME

from wx import BeginBusyCursor
from wx import EndBusyCursor
from wx import ProgressDialog

from wx import Yield as wxYield

from umlextensions.IExtensionsFacade import IExtensionsFacade

from umlextensions.extensiontypes.ExtensionDataTypes import Author
from umlextensions.extensiontypes.ExtensionDataTypes import ExtensionDescription
from umlextensions.extensiontypes.ExtensionDataTypes import ExtensionName
from umlextensions.extensiontypes.ExtensionDataTypes import FileSuffix
from umlextensions.extensiontypes.ExtensionDataTypes import FormatName
from umlextensions.extensiontypes.ExtensionDataTypes import Version

from umlextensions.input.BaseInputExtension import BaseInputExtension
from umlextensions.input.InputFormat import InputFormat
from umlextensions.input.python.DlgSelectMultiplePackages import DlgSelectMultiplePackages
from umlextensions.input.python.PythonParseException import PythonParseException

FORMAT_NAME:           FormatName           = FormatName("Python File(s)")
FILE_SUFFIX:           FileSuffix           = FileSuffix('py')
EXTENSION_DESCRIPTION: ExtensionDescription = ExtensionDescription('Python code reverse engineering')

class InputPython(BaseInputExtension):

    def __init__(self, extensionsFacade: IExtensionsFacade):

        super().__init__(extensionsFacade)
        self.logger: Logger = getLogger(__name__)

        self._name    = ExtensionName('Python to UML')
        self._author  = Author('Humberto A. Sanchez II')
        self._version = Version('3.0')

        self._inputFormat  = InputFormat(formatName=FORMAT_NAME, fileSuffix=FILE_SUFFIX, description=EXTENSION_DESCRIPTION)

        self._packageCount:   int = 0
        self._moduleCount:    int = 0
        self._importPackages: int = 0

        self._readProgressDlg: ProgressDialog = cast(ProgressDialog, None)

    def setImportOptions(self) -> bool:

        """
        We do need to ask for the input file names

        Returns:  'True', we support import
        """
        startDirectory: str = self._preferences.startDirectory
        with DlgSelectMultiplePackages(startDirectory=startDirectory, inputFormat=self.inputFormat) as dlg:
            if dlg.ShowModal() == OK:
                self._packageCount   = dlg.packageCount
                self._moduleCount    = dlg.moduleCount
                self._importPackages = dlg.importPackages

                return True
            else:
                return False

    def read(self) -> bool:

        BeginBusyCursor()
        wxYield()
        status: bool = True
        try:
            self._readProgressDlg = ProgressDialog('Parsing Files', 'Starting', parent=None, style=PD_APP_MODAL | PD_ELAPSED_TIME)

            # reverseEngineer: ReverseEngineerPythonV3 = ReverseEngineerPythonV3()

            self._readProgressDlg.SetRange(self._moduleCount)
        except (ValueError, Exception, PythonParseException) as e:
            self._readProgressDlg.Destroy()

            MessageBox(f'{e}', 'Error', OK | ICON_ERROR)
            status = False
        else:
            self._readProgressDlg.Destroy()
            self._extensionsFacade.extensionModifiedProject()
        finally:
            EndBusyCursor()
            self._extensionsFacade.refreshFrame()
            wxYield()

        return status
