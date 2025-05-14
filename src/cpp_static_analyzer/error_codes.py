""" Error codes. """

from enum import Enum

class ErrorCodes(Enum):
    """ Error codes. """

    # General errors
    SUCCESS = 0
    ERROR = 1

    # File errors
    FILE_NOT_FOUND = 10
    FILE_EXIST = 11
    FILE_READ_ERROR = 12
    FILE_WRITE_ERROR = 13
