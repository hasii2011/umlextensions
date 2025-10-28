
from typing import Dict
from typing import NewType

from codeallybasic.UnitTestBase import UnitTestBase

from pyutmodelv2.PyutField import PyutField
from pyutmodelv2.PyutField import PyutFields

PyutFieldHashIndex  = NewType('PyutFieldHashIndex',  Dict[str, PyutField])


class BaseTestPythonPegVisitor(UnitTestBase):
    """
    Copied and modified from the pyutplugins project
    """

    RESOURCES_TEST_CLASSES_PACKAGE_NAME: str = f'{UnitTestBase.RESOURCES_PACKAGE_NAME}.testclasses.python'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def _makeFieldIndex(self, pyutFields: PyutFields) -> PyutFieldHashIndex:

        fieldIndex: PyutFieldHashIndex = PyutFieldHashIndex({})
        for field in pyutFields:
            fieldIndex[field.name] = field

        return fieldIndex
