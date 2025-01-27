from hashlib import sha256


def hash(input: bytearray) -> bytearray:
    """
    Builds the SHA-256 hash

    :param input: The content to hash
    :type input: bytearray
    :return: The hashed digest
    :rtype: bytearray
    """
    h = sha256()
    h.update(input)
    return h.digest()


def string2bytearray(string: str, encoding="utf-8") -> bytearray:
    """
    Transforms the passed string to a byte array

    :param string: The input string to transform
    :type string: str
    :param encoding: The encoding used in the string [default: utf-8]
    :type encoding: str
    :return: The bytes
    :rtype: bytearray
    """
    return bytearray(str.encode(string, encoding))
