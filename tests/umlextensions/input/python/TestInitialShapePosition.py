
import unittest

from umlshapes.types.UmlPosition import UmlPosition

from umlextensions.input.python.InitialShapePosition import InitialShapePosition


class TestInitialShapePosition(unittest.TestCase):

    def testDeSerializeValid(self):
        position: UmlPosition = InitialShapePosition.deSerialize('140,147')
        self.assertEqual(position.x, 140)
        self.assertEqual(position.y, 147)

    def testDeSerializeInvalidFormat(self):
        with self.assertRaisesRegex(AssertionError, 'Incorrectly formatted position'):
            InitialShapePosition.deSerialize('140')

        with self.assertRaisesRegex(AssertionError, 'Incorrectly formatted position'):
            InitialShapePosition.deSerialize('140,147,200')

    def testDeSerializeNonNumeric(self):
        with self.assertRaisesRegex(AssertionError, 'String must be numeric'):
            InitialShapePosition.deSerialize('140,abc')

    def testStr(self):
        position: InitialShapePosition = InitialShapePosition(x=140, y=147)
        self.assertEqual(str(position), '140,147')


if __name__ == '__main__':
    unittest.main()
