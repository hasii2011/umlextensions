
import logging
import logging.config

import json

from click import command
from click import option
from click import version_option
from codeallybasic.UnitTestBase import UnitTestBase

from wx import App


__version__ = "3.0.0"

from codeallybasic.UnitTestBase import JSON_LOGGING_CONFIG_FILENAME

from tests.extensiondemo.ExtensionFrame import ExtensionFrame


class ExtensionTestApp(App):

    WINDOW_WIDTH:  int = 900
    WINDOW_HEIGHT: int = 500

    def __init__(self, redirect: bool = False, createEmptyProject: bool = True):

        self._createEmtpyProject: bool = createEmptyProject

        super(ExtensionTestApp, self).__init__(redirect=redirect)

    def OnInit(self) -> bool:

        ExtensionTestApp.setUpLogging()

        # noinspection PyAttributeOutsideInit
        self._frameTop: ExtensionFrame = ExtensionFrame()

        self._frameTop.Show(True)

        return True

    @classmethod
    def setUpLogging(cls):
        """"""
        loggingConfigFilename: str = cls.findLoggingConfig()

        with open(loggingConfigFilename, 'r') as loggingConfigurationFile:
            configurationDictionary = json.load(loggingConfigurationFile)

        logging.config.dictConfig(configurationDictionary)
        logging.logProcesses = False
        logging.logThreads = False

    @classmethod
    def findLoggingConfig(cls) -> str:

        fqFileName: str = UnitTestBase.getFullyQualifiedResourceFileName(UnitTestBase.RESOURCES_PACKAGE_NAME, JSON_LOGGING_CONFIG_FILENAME)

        return fqFileName

    def loadXmlFile(self, fqFileName: str):
        """

        Args:
            fqFileName: full qualified file name
        """
        # self._frameTop.loadXmlFile(fqFileName=fqFileName)
        pass


@command()
@version_option(version=f'{__version__}', message='%(version)s')
@option('-i', '--input-file', required=False, help='The input .xml file to preload on startup.')
def commandHandler(input_file: str):

    if input_file is not None:
        testApp: ExtensionTestApp = ExtensionTestApp(redirect=False, createEmptyProject=False)
        testApp.loadXmlFile(input_file)
    else:
        testApp = ExtensionTestApp(redirect=False)

    testApp.MainLoop()


if __name__ == "__main__":
    commandHandler()
