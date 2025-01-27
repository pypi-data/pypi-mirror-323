from unittest import TestCase

from gridding import KILOMETER, METER, FR, GPS, Grid, Resolution


class TestGrid(TestCase):
    grid = Grid(Resolution(200, METER))

    def test_from_address(self):
        code, tile = self.grid.from_address(
            " 9, boulevard Gouvion Saint-Cyr - 75017 Paris",
            FR(filepath="../../data/fr_address_repository_test.csv"),
        )
        self.assertEqual(code, "WGS84|RES200m|N4888412|E0228838")
        self.assertEqual(tile.to_string(), "4205.2717")

    def test_from_gps(self):
        code, tile = self.grid.from_gps(GPS(2, 45))
        self.assertEqual(code, "WGS84|RES200m|N4499997|E0199811")
        self.assertEqual(tile.to_string(), "2046.2807")
        close_point, _ = self.grid.from_gps(GPS(2.0005, 45.0005))
        self.assertEqual(code, close_point)
        off_grid, off_tile = self.grid.from_gps(GPS(-5.151, 41.317))
        self.assertEqual(off_grid, "WGS84|RES200m|N4131666|W0515111")
        self.assertEqual(off_tile.to_string(), "0.0")
        off_grid, off_tile = self.grid.from_gps(GPS(-5.152, 41.316))
        self.assertEqual(off_grid, "WGS84|RES200m|N4131486|W0515351")
        self.assertEqual(off_tile.to_string(), "-1.-1")
        off_grid, off_tile = self.grid.from_gps(GPS(-10, -6))
        self.assertEqual(off_grid, "WGS84|RES200m|S0600171|W1000119")
        self.assertEqual(off_tile.to_string(), "-26197.-2674")

    def test_get_tile(self):
        tile = self.grid.get_tile("WGS84|RES200m|N4499997|E0199811")
        self.assertEqual(tile.to_string(), "2046.2807")
        self.assertEqual(tile.x(), 2807)
        self.assertEqual(tile.y(), 2046)


class TestResolution(TestCase):
    def test_to_string(self):
        res = Resolution(200, METER)
        self.assertEqual(res.to_string(), "RES200m")
        res = Resolution(1, KILOMETER)
        self.assertEqual(res.to_string(), "RES1km")
        with self.assertRaises(Exception):
            Resolution(50, "cl")
