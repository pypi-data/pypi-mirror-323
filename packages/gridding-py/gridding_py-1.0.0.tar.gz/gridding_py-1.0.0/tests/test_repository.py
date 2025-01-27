from unittest import TestCase

from gridding import FR


class TestRepository(TestCase):
    def test_address2gps(self):
        france = FR(filepath="../../data/fr_address_repository_test.csv")
        self.assertTrue(
            france.csv_filepath().endswith("fr_address_repository_test.csv")
        )
        gps = france.address2gps(" 9, boulevard Gouvion Saint-Cyr - 75017 Paris")
        self.assertEqual(gps.x(), 2.29064)
        self.assertEqual(gps.y(), 48.884847)
        with self.assertRaises(Exception):
            france.gps2address()
