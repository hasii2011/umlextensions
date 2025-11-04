
from logging import Logger
from logging import getLogger


class SimpleClassMagicMethods:
    def __init__(self):
        self.logger: Logger = getLogger(__name__)

    def __str__(self) -> str:
        return 'I am me'

    def __repr__(self) -> str:
        return f'SimpleClassMagicMethods - {id(self)}'
