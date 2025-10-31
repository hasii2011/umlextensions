
from logging import Logger
from logging import getLogger

from umlextensions.IExtensionAdapter import IExtensionAdapter
from umlextensions.extensiontypes.BaseExtension import BaseExtension


class BaseToolExtension(BaseExtension):
    """
    Base class for extensions that can manipulate UML diagrams.  Examples,
    include but are not limited to:

        * Various layouts (Sugiyama, Orthogonal, Force Directed
        * Arranging non crossing links
        * Arranging orthogonal links
    """
    def __init__(self, extensionAdapter: IExtensionAdapter):

        super().__init__(extensionAdapter)
        self.logger: Logger = getLogger(__name__)
