
from sys import exc_info

from traceback import StackSummary
from traceback import extract_stack
from traceback import format_list

import stackprinter

from umlextensions.StackTraceFormatter import StackTraceFormatter
from umlextensions.StackTraceFormatter import StackTraceList


class ErrorFormatter:
    """
    A static class with class methods to simplify error reporting
    """
    def __init__(self):
        pass

    @classmethod
    def getError(cls) -> str:
        """
        TODO:
        This needs to be moved to code ally basic

        Returns:
            System exception information as a formatted string
        """
        error, eMessage, eTraceback = exc_info()
        return str(error)

    @classmethod
    def getErrorMessage(cls):
        error, eMessage, eTraceback = exc_info()
        return str(eMessage)

    @classmethod
    def getFormattedStack(cls) -> str:
        """

        Returns: Very detailed stack information
        """
        return stackprinter.format()

    @classmethod
    def getSimpleStack(cls) -> str:
        """

        Returns:  A simpler homegrown stack print
        """
        stackSummary:        StackSummary        = extract_stack()
        stackTraceList:      StackTraceList      = format_list(stackSummary)
        stackTraceFormatter: StackTraceFormatter = StackTraceFormatter(stackTraceList=stackTraceList)

        bigString: str = stackTraceFormatter.dumpedStackList()

        return bigString
