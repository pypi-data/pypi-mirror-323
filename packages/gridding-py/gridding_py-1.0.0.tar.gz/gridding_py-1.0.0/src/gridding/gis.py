import math


class GIS:
    """
    Defines the interface for a Geodesic Information System (GIS), eg. `WGS84` or `RGF93`
    """

    def d_lat(self, latitude: float) -> float:
        """
        :return: The distance in meter for one degree in latitude expressed in degrees
        :rtype: float
        """
        pass

    def d_lon(self, latitude: float) -> float:
        """
        :return: The distance in meter for one degree in longitude at the passed latitude expressed in degrees
        :rtype: float
        """
        pass

    def delta_latitude(self, distance: float, latitude: float) -> float:
        """
        :return: The degrees covered by the distance in meter around the given latitude expressed in degrees
        :rtype: float
        """
        pass

    def delta_longitude(
        self, distance: float, longitude: float, latitude: float
    ) -> float:
        """
        :return: The degrees covered by the distance in meter at the given longitude and latitude expressed in degrees
        :rtype: float
        """
        pass

    def get_a(self) -> float:
        """
        :return: The semi-major axis `a` of the system
        :rtype: float
        """
        pass

    def get_e(self) -> float:
        """
        :return: The excentricity `e` of the system
        :rtype: float
        """
        pass

    def get_k0(self) -> float:
        """
        :return: The UTM scale factor `k0` for the system
        :rtype: float
        """
        pass

    def get_lambda0(self, longitude: float) -> float:
        """
        :return: The UTM zone's central longitude `lambda0` in radians for the passed longitude expressed in degrees
        :rtype: float
        """
        pass

    def name(self) -> str:
        """
        :return: The code name of the GIS
        :rtype: str
        """
        pass


class WGS84(GIS):
    """
    Implementation of the WGS-84 geodesic system
    """

    a = float(6378137)
    b = float(6356752.3142)
    k0 = float(0.9996)

    def __init__(self):
        self.e = math.sqrt(1 - math.pow(self.b, 2) / math.pow(self.a, 2))

    def d_lat(self, latitude: float) -> float:
        return (
            math.pi
            * (self.a * (1 - math.pow(self.e, 2)))
            / math.pow(
                1 - math.pow(self.e, 2) * math.pow(math.sin(math.radians(latitude)), 2),
                3 / 2,
            )
            / 180
        )

    def d_lon(self, latitude: float) -> float:
        return (
            math.pi
            * self.a
            * math.cos(math.radians(latitude))
            / 180
            / math.sqrt(
                1 - math.pow(self.e, 2) * math.pow(math.sin(math.radians(latitude)), 2)
            )
        )

    def delta_latitude(self, distance: float, latitude: float) -> float:
        return distance / self.d_lat(latitude)

    def delta_longitude(
        self, distance: float, longitude: float, latitude: float
    ) -> float:
        return distance / (self.d_lon(latitude) * math.cos(math.radians(longitude)))

    def get_a(self) -> float:
        return self.a

    def get_e(self) -> float:
        return self.e

    def get_k0(self) -> float:
        return self.k0

    def get_lambda0(self, longitude: float) -> float:
        return (
            math.radians(math.floor(longitude / 6) * 6 + 3)
            if longitude > 0
            else math.radians(math.ceil(longitude / 6) * 6 - 3)
        )

    def name(self) -> str:
        return "WGS84"
