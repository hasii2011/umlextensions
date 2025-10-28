
from logging import Logger
from logging import getLogger


class BaseExtension:
    """
    Contains common behavior and attributes for the various
    types of extensions
    """
    def __init__(self):
        self._baseLogger: Logger = getLogger(__name__)
