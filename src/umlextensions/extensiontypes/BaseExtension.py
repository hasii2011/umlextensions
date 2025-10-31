
from logging import Logger
from logging import getLogger

from wx import OK
from wx import ICON_ERROR

from wx import MessageDialog

from umlextensions.IExtensionAdapter import IExtensionAdapter
from umlextensions.extensiontypes.ExtensionDataTypes import Author
from umlextensions.extensiontypes.ExtensionDataTypes import ExtensionName
from umlextensions.extensiontypes.ExtensionDataTypes import Version


class BaseExtension:
    """
    Contains common behavior and attributes for the various
    types of extensions
    """
    def __init__(self, extensionAdapter: IExtensionAdapter):

        self._extensionAdapter: IExtensionAdapter = extensionAdapter

        self._baseLogger: Logger = getLogger(__name__)

        self._name:         ExtensionName = ExtensionName('Implementor must provide the plugin name')

        self._author:       Author  = Author('Implementor must provide the plugin author')
        self._version:      Version = Version('Implementor must provide the version')

        #
        # Extension that require an active frame or frame(s) should set this value to `True`
        # Some output extension may create their own frame or their own project and frame.  These should set this value to `False`
        # Extensions should set the value they need in their constructor
        #
        self._requireActiveFrame: bool = True
        #
        # Some Output extension may offer the option of exporting only selected shape;  Others may just export
        # the entire project or the current frame
        #
        # Extensions should set the value they need in their constructor
        self._requireSelection:   bool = True
        #
        #
        # prefs: ExtensionPreferences = PyutPreferences()
        # if prefs.extensionAutoSelectAll is True:       TODO:  Need extension preferences
        #     self._autoSelectAll: bool = True

        #
        # Some extensions may need to work with all the shapes on the UML frame.  Set this
        # to true to select them all
        #
        self._autoSelectAll: bool = False

    @property
    def name(self) -> ExtensionName:
        """
        Implementations set the protected variable at class construction

        Returns:  The plugin name
        """
        return self._name

    @property
    def author(self) -> Author:
        """
        Implementations set the protected variable at class construction

        Returns:  The author's name
        """
        return self._author

    @property
    def version(self) -> Version:
        """
        Implementations set the protected variable at class construction

        Returns: The plugin version string
        """
        return self._version

    @classmethod
    def showNoUmlFrameDialog(cls):
        booBoo: MessageDialog = MessageDialog(parent=None, message='No UML frame', caption='Try Again!', style=OK | ICON_ERROR)
        booBoo.ShowModal()

    @classmethod
    def showNoSelectedUmlShapesDialog(cls):
        booBoo: MessageDialog = MessageDialog(parent=None, message='No selected UML shapes', caption='Try Again!', style=OK | ICON_ERROR)
        booBoo.ShowModal()
