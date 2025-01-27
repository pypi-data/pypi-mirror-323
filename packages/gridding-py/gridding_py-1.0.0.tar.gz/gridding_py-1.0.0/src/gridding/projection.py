import math

from gridding import GIS


class Projection:
    """
    Defines the interface to a projection system, eg. `UTM` or `Lambert93`
    """

    def from_xy(self, x: float, y: float) -> tuple[float, float]:
        """
        :param x: The X coordinate
        :type x: float
        :param y: The Y coordinate
        :type y: float
        :return: The latitude and longitude expressed in decimal degrees
        :rtype: tuple[float, float]
        """
        pass

    def to_xy(self, latitude: float, longitude: float) -> tuple[float, float]:
        """
        :param latitude: The latitude expressed in degrees
        :type latitude: float
        :param longitude: The longitude expressed in degrees
        :type longitude: float
        :return: The X and Y coordinates
        :rtype: tuple[float, float]
        """
        pass


class UTM(Projection):
    """
    Implementation of the Universal Transverse Mercator (UTM) projection
    """

    def __init__(self, gis: GIS):
        self.gis = gis

    def from_xy(self, x, y):
        return super().from_xy(x, y)  # TODO

    def to_xy(self, latitude: float, longitude: float) -> tuple[float, float]:
        phi = math.radians(latitude)
        lmbda = math.radians(longitude)
        e2 = math.pow(self.gis.get_e(), 2)
        N = self.gis.get_a() / math.sqrt(1 - e2 * math.pow(math.sin(phi), 2))
        T = math.pow(math.tan(phi), 2)
        C = e2 * math.pow(math.cos(phi), 2) / (1 - e2)
        A = (lmbda - self.gis.get_lambda0(longitude)) * math.cos(phi)
        e4 = math.pow(self.gis.get_e(), 4)
        e6 = math.pow(self.gis.get_e(), 6)
        M = self.gis.get_a() * (
            (1 - e2 / 4 - 3 * e4 / 64 - 5 * e6 / 256) * phi
            - (3 * e2 / 8 + 3 * e4 / 32 + 45 * e6 / 1024) * math.sin(2 * phi)
            + (15 * e4 / 256 + 45 * e6 / 1024) * math.sin(4 * phi)
            - (35 * e6 / 3072) * math.sin(6 * phi)
        )
        x = (
            self.gis.get_k0()
            * (
                N
                * (
                    A
                    + (1 - T + C) * math.pow(A, 3) / 6
                    + (5 - 18 * T + math.pow(T, 2) + 72 * C - 58 * e2)
                    * math.pow(A, 5)
                    / 120
                )
            )
            + 500000
        )
        y = self.gis.get_k0() * (
            M
            + N
            * math.tan(phi)
            * (
                math.pow(A, 2) / 2
                + (5 - T + 9 * C + 4 * math.pow(C, 2)) * math.pow(A, 4) / 24
                + (61 - 58 * T + math.pow(T, 2) + 600 * C - 330 * e2)
                * math.pow(A, 6)
                / 720
            )
        )
        y = y if latitude > 0 else y + 10000000
        return x, y
