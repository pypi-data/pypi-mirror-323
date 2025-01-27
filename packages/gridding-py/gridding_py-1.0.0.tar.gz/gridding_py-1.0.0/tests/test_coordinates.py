import math
from unittest import TestCase

from gridding import GPS, Tile, XY


class TestCoordinates(TestCase):
    def test_gps(self):
        lat = 45
        lon = 2
        gps = GPS(lon, lat)
        self.assertEqual(gps.x(), lon)
        self.assertEqual(gps.y(), lat)

    def test_tile(self):
        row = 1234
        column = 5678
        tile1 = Tile(column, row)
        self.assertEqual(tile1.x(), column)
        self.assertEqual(tile1.y(), row)
        self.assertEqual(tile1.to_string(), "1234.5678")

        tile2 = Tile(5676, 1236)  # Two in each direction
        distance = Tile.Distance(tile1, tile2)
        self.assertEqual(distance, 2)

        tile = Tile.FromString(tile1.to_string())
        self.assertEqual(tile, tile1)

    def test_xy(self):
        x = 123456.7
        y = 890123.4
        xy = XY(x, y)
        self.assertEqual(xy.x(), x)
        self.assertEqual(xy.y(), y)
        self.assertEqual(xy.projection, "UTM")
        self.assertEqual(xy.gis, "WGS84")
