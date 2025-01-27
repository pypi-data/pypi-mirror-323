import math
from unittest import TestCase

from gridding import WGS84


class TestWGS84(TestCase):
    gis = WGS84()

    def test_d_lat(self):
        d_lat = self.gis.d_lat(45)
        self.assertEqual(d_lat, 111131.77741377673)

    def test_d_lon(self):
        d_lat = self.gis.d_lon(45)
        self.assertEqual(d_lat, 78846.83509425736)

    def test_delta_latitude(self):
        degrees = self.gis.delta_latitude(200, 45)
        self.assertEqual(degrees, 0.0017996652681558434)

    def test_delta_longitude(self):
        degrees = self.gis.delta_longitude(200, 2, 45)
        self.assertEqual(degrees, 0.0025381095971769674)

    def test_get_lambda0(self):
        radians = self.gis.get_lambda0(2)
        self.assertEqual(radians, math.radians(3))
        radians = self.gis.get_lambda0(-7)
        self.assertEqual(radians, math.radians(-9))

    def test_name(self):
        self.assertEqual(self.gis.name(), "WGS84")
