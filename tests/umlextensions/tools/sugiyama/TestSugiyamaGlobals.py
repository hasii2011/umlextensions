
from unittest import main
from unittest.mock import MagicMock
from unittest.mock import patch

from typing import List
from typing import Tuple

from codeallybasic.UnitTestBase import UnitTestBase

from umlextensions.IExtensionsFacade import IExtensionsFacade
from umlextensions.tools.sugiyama.SugiyamaGlobals import SugiyamaGlobals
from umlextensions.tools.sugiyama.SugiyamaGlobals import cmp
from umlextensions.tools.sugiyama.SugiyamaNode import SugiyamaNode
from umlextensions.tools.sugiyama.VirtualSugiyamaNode import VirtualSugiyamaNode


class TestSugiyamaGlobals(UnitTestBase):
    """
    Unit tests for SugiyamaGlobals and cmp helper function.
    """

    def testCmp(self):
        """
        Verify cmp returns -1 when left < right, 0 when equal, and 1 when left > right.
        """
        self.assertEqual(cmp(2, 5), -1)
        self.assertEqual(cmp(5, 5), 0)
        self.assertEqual(cmp(9, 5), 1)

    def testCmpIndexWithNoneNeighbors(self):
        """
        Verify cmpIndex returns 0 when either leftNode or rightNode is None.
        """
        centerNode: VirtualSugiyamaNode = VirtualSugiyamaNode()
        neighborNode: VirtualSugiyamaNode = VirtualSugiyamaNode()
        neighborNode.index = 3

        tupleBothNone: Tuple[SugiyamaNode, None] = (centerNode, None)
        self.assertEqual(SugiyamaGlobals.cmpIndex(tupleBothNone), 0)

        centerNode.leftNode = neighborNode
        centerNode.rightNode = None
        self.assertEqual(SugiyamaGlobals.cmpIndex(tupleBothNone), 0)

        centerNode.leftNode = None
        centerNode.rightNode = neighborNode
        self.assertEqual(SugiyamaGlobals.cmpIndex(tupleBothNone), 0)

    def testCmpIndexWithBothNeighbors(self):
        """
        Verify cmpIndex compares leftNode.index and rightNode.index when both exist.
        """
        centerNode: VirtualSugiyamaNode = VirtualSugiyamaNode()
        leftNeighbor: VirtualSugiyamaNode = VirtualSugiyamaNode()
        rightNeighbor: VirtualSugiyamaNode = VirtualSugiyamaNode()

        centerNode.leftNode = leftNeighbor
        centerNode.rightNode = rightNeighbor
        edgeTuple: Tuple[SugiyamaNode, None] = (centerNode, None)

        leftNeighbor.index = 1
        rightNeighbor.index = 4
        self.assertEqual(SugiyamaGlobals.cmpIndex(edgeTuple), -1)

        leftNeighbor.index = 4
        rightNeighbor.index = 4
        self.assertEqual(SugiyamaGlobals.cmpIndex(edgeTuple), 0)

        leftNeighbor.index = 7
        rightNeighbor.index = 2
        self.assertEqual(SugiyamaGlobals.cmpIndex(edgeTuple), 1)

    def testCmpBarycenterReturnsZeroWhenNone(self):
        """
        Verify cmpBarycenter returns 0 when theNode.barycenter is None.
        """
        node: VirtualSugiyamaNode = VirtualSugiyamaNode()
        self.assertIsNone(node.barycenter)
        self.assertEqual(SugiyamaGlobals.cmpBarycenter(node), 0)

    def testCmpBarycenterReturnsBarycenterValue(self):
        """
        Verify cmpBarycenter returns theNode.barycenter when set.
        """
        node: VirtualSugiyamaNode = VirtualSugiyamaNode()
        node._barycenter = 7
        self.assertEqual(SugiyamaGlobals.cmpBarycenter(node), 7)

    def testListNodesSortWithCmpBarycenter(self):
        """
        Verify listNodes.sort(key=SugiyamaGlobals.cmpBarycenter) orders nodes ascending by barycenter.
        """
        nodeHigh: VirtualSugiyamaNode = VirtualSugiyamaNode()
        nodeLow: VirtualSugiyamaNode = VirtualSugiyamaNode()
        nodeMid: VirtualSugiyamaNode = VirtualSugiyamaNode()

        nodeHigh._barycenter = 9
        nodeLow._barycenter = 1
        nodeMid._barycenter = 4

        listNodes: List[SugiyamaNode] = [nodeHigh, nodeLow, nodeMid]
        listNodes.sort(key=SugiyamaGlobals.cmpBarycenter)

        self.assertEqual(listNodes, [nodeLow, nodeMid, nodeHigh])

    @patch('umlextensions.tools.sugiyama.SugiyamaGlobals.wxYield')
    @patch('umlextensions.tools.sugiyama.SugiyamaGlobals.MessageBox')
    def testWaitKey(self, mockMessageBox: MagicMock, mockWxYield: MagicMock):
        """
        Verify waitKey displays default or custom message, refreshes frame, and yields wx event loop.
        """
        mockFacade: MagicMock = MagicMock(spec=IExtensionsFacade)

        SugiyamaGlobals.waitKey(extensionsFacade=mockFacade, optionalMessage=None)
        mockMessageBox.assert_called_once()
        mockFacade.refreshFrame.assert_called_once()
        mockWxYield.assert_called_once()

        mockMessageBox.reset_mock()
        mockFacade.refreshFrame.reset_mock()
        mockWxYield.reset_mock()

        SugiyamaGlobals.waitKey(extensionsFacade=mockFacade, optionalMessage='Step completed')
        mockMessageBox.assert_called_once()
        mockFacade.refreshFrame.assert_called_once()
        mockWxYield.assert_called_once()


if __name__ == '__main__':
    main()
