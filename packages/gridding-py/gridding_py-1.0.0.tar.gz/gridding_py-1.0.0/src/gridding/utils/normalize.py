import os
import re


FR_DICTIONARY = "fr_dictionary.txt"


class Normalizer:
    """
    Utility to normalize a full postal address

    IMPORTANT: It does not validate the input format, only transforms it
    """

    dictionary = dict()

    def __init__(self, filepath: str = None):
        if not filepath:
            filepath = os.path.join(os.path.dirname(__file__), FR_DICTIONARY)
        with open(filepath, "r") as f:
            for line in f:
                [word, substitution] = line.split("\t", 2)
                self.dictionary[word] = substitution

    def normalize(self, address: str) -> str:
        """
        Builds the normalized address

        :param address: The input address string
        :type address: str
        :return: The normalized address
        :rtype: str
        """
        return normalize(address, self.dictionary)


def normalize(address: str, dictionary: dict) -> str:
    """
    Builds a full address normalized using the passed dictionary

    :param address: The input address string
    :type address: str
    :param dictionary: The dictionary object with key/value respectively being the word to search and the word to substitute to it
    :type dictionary: dict
    :return: The normalized string
    :rtype: str
    """
    # Remove all punctuation and put in lower case
    normalized = re.sub(
        r"[\s\.,;:\/\\'\"\-_\(\)$+=\n\t]+", " ", address.lower()
    ).strip()
    # Replace accented characters
    normalized = normalized.translate(
        str.maketrans("àäãâçéèêëìïîôöòùûüñ", "aaaaceeeeiiiooouuun")
    )
    # Get rid of final numbers in the ending city name (arrondissement, cedex, ...)
    normalized = re.sub(r"[0-9]+$", "", normalized)
    # Separate eventual repetitor from street number
    normalized = re.sub(r"^(\d+)([a-z]*)\s(.*)", r"\1 \2 \3", normalized)
    return substitute(normalized, dictionary)


def substitute(input: str, dictionary: dict) -> str:
    words = input.split(" ")
    output = []
    for word in words:
        output.append(dictionary[word] if word in dictionary.keys() else word)
    return re.sub(r"\s+", " ", " ".join(output)).strip()
