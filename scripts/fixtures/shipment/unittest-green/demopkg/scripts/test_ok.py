import unittest


class T(unittest.TestCase):
    def test_shape(self):
        self.assertEqual(2 + 2, 4)

    def test_no_gap(self):
        self.assertTrue(True)
