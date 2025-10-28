
from logging import Logger
from logging import getLogger

from umlextensions.BaseExtension import BaseExtension


class BaseInputExtension(BaseExtension):
    """
    Base class for extensions that can convert foreign structured
    data into UML Diagrams.  Examples include but are not limited to:
        * DTDs
        * Java code
        * Python code
    """
    def __init__(self):
        super().__init__()
        self.logger: Logger = getLogger(__name__)
