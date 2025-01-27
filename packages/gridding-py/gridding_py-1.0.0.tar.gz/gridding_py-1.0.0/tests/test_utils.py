from unittest import TestCase

from gridding import hash, normalize, Normalizer, string2bytearray


class TestUtils(TestCase):
    def test_normalize(self):
        dictionary = Normalizer().dictionary
        normalized = normalize(
            " 9, boulevard Gouvion Saint-Cyr - 75017 Paris.", dictionary
        )
        self.assertEqual(normalized, "9 bd gouvion st cyr 75017 paris")
        normalized = normalize(
            """
24bis, boulevar GOUVION ST-CYR
75000 PARIS Cedex 17
""",
            dictionary,
        )
        self.assertEqual(normalized, "24 b bd gouvion st cyr 75000 paris")

    def test_hash(self):
        hashed = hash(string2bytearray("This is a test"))
        hex = hashed.hex()
        self.assertEqual(
            hex, "c7be1ed902fb8dd4d48997c6452f5d7e509fbcdbe2808b16bcf4edce4c07d14e"
        )
