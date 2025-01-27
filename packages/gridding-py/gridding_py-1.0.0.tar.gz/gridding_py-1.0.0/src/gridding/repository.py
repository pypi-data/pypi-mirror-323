import csv
from typing import Callable

from gridding import GPS, hash, Normalizer, string2bytearray


class Repository:
    """
    Defines the interface of a repository
    """

    def csv_filepath(self) -> str:
        """
        Get the path to the CSV file serving as the repository

        In order to be correctly unpacked, it must contain data in the following format per line:
        &lt;hexadecimal hash of normalized data&gt;,&lt;latitude&gt;,&lt;longitude&gt;

        IMPORTANT:
        - The hash engine and the normalizing functions must be consistent over time
        - The latitude and longitude must be expressed in decimal degrees
        """
        pass


class PostalAddress(Repository):
    """
    Defines the interface for a postal address repository
    """

    def address2gps(self, full_address: str) -> GPS:
        """
        :param full_address: The full stringified address
        :type full_address: str
        :return: The GPS coordinates
        :rtype: GPS
        """
        pass

    def gps2address(self, coordinates: GPS, directory: dict) -> str:
        """
        Returns the full address as a one-liner string from the passed GPS coordinates

        It expects a directory of postal addresses holding the correspondence
        between the hexadecimal hash of the normalized address and the actual one-liner address

        :param coordinates: The GPS coordinates
        :type coordinates: GPS
        :param directory: The key/value directory to use as reference
        :type directory: dict
        :return: The one-liner address if found
        :rtype: str
        """
        pass


DEFAULT_FR_CSV = "./data/fr_address_repository.csv"


class FR(PostalAddress):
    """
    The French open repository of postal addresses is defined by:
    - the filepath to the CSV holding the data
    - the hash function used for the normalized address
    - the normalizing function used to homogenize any input address

    @see https://adresse.data.gouv.fr/donnees-nationales
    """

    data = dict()

    def __init__(
        self,
        filepath: str = DEFAULT_FR_CSV,
        hash_function: Callable[[bytearray], bytearray] = hash,
        normalizer: Callable[[str], str] = Normalizer().normalize,
    ):
        self.filepath = filepath
        self.hash_function = hash_function
        self.normalizer = normalizer
        try:
            with open(self.filepath, "r") as f:
                for line in csv.reader(f):
                    hash_norm, lat, lon = line
                    self.data[hash_norm] = GPS(float(lon), float(lat))
        except Exception as e:
            print(
                """Unable to locate the CSV file: make sure it exists.
You may download the default file (https://huggingface.co/datasets/cyrildever/gridding/blob/main/fr_address_repository.csv.gz)
and unzip it under a './data/' directory at root."""
            )
            raise e

    def address2gps(self, full_address: str) -> GPS:
        return self.data[
            self.hash_function(string2bytearray(self.normalizer(full_address))).hex()
        ]

    def gps2address(self, coordinates: GPS, directory: dict) -> str:
        raise Exception("not implement yet")

    def csv_filepath(self) -> str:
        return self.filepath
