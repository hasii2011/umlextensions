
from typing import Dict
from typing import NewType

from codeallybasic.UnitTestBase import UnitTestBase

from umlmodel.Field import Field
from umlmodel.Field import Fields

ModelFieldHashIndex  = NewType('ModelFieldHashIndex', Dict[str, Field])


class BaseTestPythonPegVisitor(UnitTestBase):
    """
    """

    RESOURCES_TEST_CLASSES_PACKAGE_NAME: str = f'{UnitTestBase.RESOURCES_PACKAGE_NAME}.testclasses.python'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def _makeFieldIndex(self, modelFields: Fields) -> ModelFieldHashIndex:

        fieldIndex: ModelFieldHashIndex = ModelFieldHashIndex({})
        for field in modelFields:
            fieldIndex[field.name] = field

        return fieldIndex
