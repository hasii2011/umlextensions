
import unittest

from umlextensions.tools.orthogonallayout.LayoutAreaDimensions import LayoutAreaDimensions

class TestLayoutAreaDimensions(unittest.TestCase):

    def testDeSerializeValid(self):
        dimensions = LayoutAreaDimensions.deSerialize("800,600")
        self.assertEqual(dimensions.width, 800)
        self.assertEqual(dimensions.height, 600)

    def testDeSerializeInvalidFormat(self):
        with self.assertRaisesRegex(ValueError, "Incorrectly formatted dimensions"):
            LayoutAreaDimensions.deSerialize("800")
        
        with self.assertRaisesRegex(ValueError, "Incorrectly formatted dimensions"):
            LayoutAreaDimensions.deSerialize("800,600,400")

    def testDeSerializeNonNumeric(self):
        with self.assertRaisesRegex(ValueError, "String must be numeric"):
            LayoutAreaDimensions.deSerialize("800,abc")

    def testStr(self):
        dimensions = LayoutAreaDimensions(1024, 768)
        self.assertEqual(str(dimensions), "1024,768")


if __name__ == '__main__':
    unittest.main()
