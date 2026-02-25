
from os import sep as osSep

from pathlib import Path

from subprocess import CompletedProcess
from subprocess import run as subProcessRun

from codeallyadvanced.ui.UnitTestBaseW import UnitTestBaseW
from codeallybasic.UnitTestBase import UnitTestBase

DEBUG_FAILURE: bool = True


class ProjectTestBase(UnitTestBaseW):

    RESOURCES_TEST_CLASSES_PACKAGE_NAME: str = f'{UnitTestBase.RESOURCES_PACKAGE_NAME}.testclasses'
    RESOURCES_TEST_DATA_PACKAGE_NAME:    str = f'{UnitTestBase.RESOURCES_PACKAGE_NAME}.testdata'

    GOLDEN_GML_PACKAGE_NAME:     str = f'{RESOURCES_TEST_DATA_PACKAGE_NAME}.gmlgolden'      # noqa

    EXTERNAL_DIFF:     str = '/usr/bin/diff --normal --color=always '
    EXTERNAL_CLEAN_UP: str = 'rm '

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    @classmethod
    def runDiff(cls, goldenPackageName: str, baseFileName: str) -> int:
        """
        Assumes the caller use our ._constructGeneratedName method to get
        a fully qualified file name

        Args:
            goldenPackageName:  The package name where the gold file resides
            baseFileName:  The base file name

        Returns:  The results of the difference
        """
        goldenFileName: str = ProjectTestBase.getFullyQualifiedResourceFileName(goldenPackageName, baseFileName)
        generatedFileName: str = cls.constructGeneratedName(baseFileName=baseFileName)

        # status: int = osSystem(f'{ProjectTestBase.EXTERNAL_DIFF} {goldenFileName} {generatedFileName}')
        command:          str              = f'{ProjectTestBase.EXTERNAL_DIFF} {goldenFileName} {generatedFileName}'
        completedProcess: CompletedProcess = subProcessRun([command], shell=True, capture_output=True, text=True, check=False)

        if DEBUG_FAILURE is True and completedProcess.returncode != 0:
            print(f'{completedProcess.stderr=}')
            print(f'{completedProcess.stdout=}')

        return completedProcess.returncode

    @classmethod
    def constructGeneratedName(cls, baseFileName: str) -> str:
        """
        Constructs a full path name for a file that will be used for a unit test.
        Currently, just uses /tmp

        Args:
            baseFileName:

        Returns:    Fully qualified file name

        """

        generatedFileName: str = f'{cls.getTemporaryDirectory()}{baseFileName}'
        return generatedFileName

    @classmethod
    def getTemporaryDirectory(cls) -> str:
        return f'{osSep}tmp{osSep}'

    @classmethod
    def cleanupGenerated(cls, fileName: str):

        generatedFileName: str = cls.constructGeneratedName(baseFileName=fileName)

        path: Path = Path(generatedFileName)

        # cls.clsLogger.info(f'{path} - exists: {path.exists()}')    # does not work for TestJavaWriter
        if path.exists() is True:
            path.unlink()
