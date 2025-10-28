
from logging import Logger
from logging import getLogger


class ExtensionManager:
    """
    Manages the various extensions provided by module
        InputExtension
        OutputExtension
        ToolExtension
    """
    def __init__(self):
        self.logger: Logger = getLogger(__name__)
