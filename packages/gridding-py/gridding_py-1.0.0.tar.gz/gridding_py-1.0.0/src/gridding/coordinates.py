import math


class Coordinates:
    """
    Defines the interface for a 3-D coordinate system
    """

    def x(self) -> float:
        """
        :return: The "horizontal" coordinate, eg. longitude, X, width, left/right, column...
        :rtype: float
        """
        pass

    def y(self) -> float:
        """
        :return: The "vertical" coordinate, eg. latitude, Y, height, top/bottom, row...
        :rtype: float
        """
        pass

    def z(self) -> None | float:
        """
        :return: The third dimension if any, eg. altitude, Z, depth, up/down, layer...
        :rtype: float
        """
        pass

    def __eq__(self, other):
        return self.x() == other.x() and self.y() == other.y() and self.z() == other.z()


class GPS(Coordinates):
    """
    Implements the GPS coordinates system
    """

    def __init__(self, longitude: float, latitude: float):
        self.__x = longitude
        self.__y = latitude

    def x(self) -> float:
        return self.__x

    def y(self) -> float:
        return self.__y

    def z(self) -> None | float:
        return None


class Tile(Coordinates):
    """
    Implements the coordinate of a tile in a Grid
    where `x` is the column and `y` is the row
    starting from the bottom-left point of the Grid
    """

    @staticmethod
    def Distance(t1: "Tile", t2: "Tile") -> float:
        """
        Computes the distance between two Tiles

        :param t1: First tile instance
        :type t1: Tile
        :param t2: Second tile instance
        :type t2: Tile
        :return: The number of tiles in each direction
        :rtype: float
        """
        return math.sqrt(
            math.pow(t2.x() - t1.x(), 2) + math.pow(t2.y() - t1.y(), 2)
        ) / math.sqrt(2)

    @staticmethod
    def FromString(coord: str) -> "Tile":
        """
        Returns the tile from the passed coordinate string

        :param coord: The &lt;row&gt;.&lt;column&gt; string representation of a Tile
        :type coord: str
        :return: The corresponding tile instance
        :rtype: Tile
        """
        row, column = coord.split(".", 2)
        return Tile(column, row)

    def __init__(self, column: int, row: int):
        self.__x = float(column)
        self.__y = float(row)

    def x(self) -> float:
        return self.__x

    def y(self) -> float:
        return self.__y

    def z(self) -> None | float:
        return None

    def to_string(self) -> str:
        """
        :return: The tile as a &lt;row&gt;.&lt;column&gt;
        :rtype: str
        """
        return f"{int(self.__y)}.{int(self.__x)}"


class XY(Coordinates):
    """
    Implements the X/Y coordinates system, naming the associated projection and geodesic systems (defaults to UTM with WGS84)
    """

    def __init__(self, x: float, y: float, projection="UTM", gis="WGS84"):
        self.__x = x
        self.__y = y
        self.projection = projection
        self.gis = gis

    def x(self) -> float:
        return self.__x

    def y(self) -> float:
        return self.__y

    def z(self) -> None | float:
        return None
