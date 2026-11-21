
from logging import Logger
from logging import getLogger

from typing import Tuple

from wx import CENTRE
from wx import OK

from wx import MessageBox

from wx import Yield as wxYield

from umlextensions.IExtensionsFacade import IExtensionsFacade
from umlextensions.tools.sugiyama.SugiyamaNode import OptionalSugiyamaNode
from umlextensions.tools.sugiyama.SugiyamaNode import SugiyamaNode


def cmp(left: int, right: int) -> int:
    """
        Python 2 replacement

    Args:
        left:
        right:

    Returns:
        -1 if left < right

        0 if left = right

        1 if left > right
    """
    return (left > right) - (left < right)


class SugiyamaGlobals:

    clsLogger: Logger = getLogger(__name__)

    @staticmethod
    def cmpIndex(aTuple: Tuple) -> int:
        """
        Internal comparison function for sorting list of parents or children by index.

        Args:
            aTuple:
        Returns:
        """
        sugiyamaNode: SugiyamaNode = aTuple[0]
        l: OptionalSugiyamaNode = sugiyamaNode.leftNode
        r: OptionalSugiyamaNode = sugiyamaNode.rightNode

        if l is None or r is None:
            return 0
        else:
            SugiyamaGlobals.clsLogger.info(f' l.index: {l.index}  r.index: {r.index}')
            return cmp(l.index, r.index)

    @staticmethod
    def cmpBarycenter(sugiyamaNode: SugiyamaNode) -> int:
        """
        Sort key function for ordering nodes on a level by their pre-computed
        barycenter value via Python 3 ``list.sort(key=SugiyamaGlobals.cmpBarycenter)``.

        During the barycenter crossing-reduction phase (``Sugiyama._sortLevel``),
        horizontal neighbor links (``leftNode`` and ``rightNode``) have not yet
        been wired (they are populated later in ``assignCoordinates``). Therefore,
        this key function extracts ``theNode.barycenter`` directly rather than
        comparing neighbor nodes, returning ``0`` as a safe fallback if ``barycenter``
        is ``None``.

        Args:
            sugiyamaNode: The SugiyamaNode being sorted.

        Returns:
            The integer barycenter value of ``theNode``, or ``0`` if ``None``.
        """
        nodeBarycenter: int | None = sugiyamaNode.barycenter
        if nodeBarycenter is None:
            return 0
        else:
            return nodeBarycenter

    @staticmethod
    def waitKey(extensionsFacade: IExtensionsFacade, optionalMessage: str | None):
        # input('Press enter to continue')
        if optionalMessage is None:
            MessageBox('Press Ok to continue', 'Confirm', style=OK | CENTRE)
        else:
            MessageBox(optionalMessage, 'Press Ok to continue', style=OK | CENTRE)
        extensionsFacade.refreshFrame()
        wxYield()
