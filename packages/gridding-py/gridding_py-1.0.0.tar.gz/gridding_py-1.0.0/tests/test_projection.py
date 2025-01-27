from unittest import TestCase

from gridding import UTM, WGS84


class TestUTM(TestCase):
    def test_to_xy(self):
        utm = UTM(WGS84())
        x, y = utm.to_xy(46.132481, 4.914282)
        self.assertEqual(x, 647872.0739330685)
        self.assertEqual(y, 5110548.44413017)


# class TestLambert93(TestCase):
#     def test_to_xy(self):
#         utm = UTM(RGF93())
#         x, y = utm.to_xy(46.132481, 4.914282)
#         self.assertEqual(x, 847780.79)
#         self.assertEqual(y, 6560977.36)
