"""
Tabular inspector panel for Sugiyama layout phases, levels, and link metrics.
"""

from typing import List

from wx import BORDER_SUNKEN
from wx import FONTFAMILY_SWISS
from wx import FONTSTYLE_NORMAL
from wx import FONTWEIGHT_BOLD
from wx import Font
from wx import ID_ANY
from wx import LC_REPORT
from wx import ListCtrl
from wx import Notebook
from wx import TE_MULTILINE
from wx import TE_READONLY
from wx import TextCtrl
from wx import Window

from wx.lib.sized_controls import SizedPanel

from tests.sugiyamavisualizer.SugiyamaStep import SugiyamaLinkSnapshot
from tests.sugiyamavisualizer.SugiyamaStep import SugiyamaNodeSnapshot
from tests.sugiyamavisualizer.SugiyamaStep import SugiyamaStepSnapshot

INSPECTOR_FONT_SIZE: int = 12


class SugiyamaInspectorPanel(SizedPanel):
    """
    Notebook panel displaying Overview, Levels, and Links tabs for the Sugiyama layout.
    """

    def __init__(self, parent: Window):
        """
        Construct the Sugiyama inspector notebook panel.

        Args:
            parent: Parent container widget.
        """
        super().__init__(parent, ID_ANY)
        self.SetSizerType('vertical')

        tableFont: Font = Font(INSPECTOR_FONT_SIZE, FONTFAMILY_SWISS, FONTSTYLE_NORMAL, FONTWEIGHT_BOLD)
        self._notebook: Notebook = Notebook(self, ID_ANY)
        self._notebook.SetSizerProps(expand=True, proportion=1)
        self._notebook.SetFont(tableFont)

        # Tab 1: Overview
        self._overviewText: TextCtrl = TextCtrl(
            self._notebook,
            ID_ANY,
            value='Select a preset and step through the Sugiyama layout phases.',
            style=TE_MULTILINE | TE_READONLY | BORDER_SUNKEN
        )
        self._overviewText.SetFont(tableFont)
        self._notebook.AddPage(self._overviewText, 'Overview')

        # Tab 2: Levels
        self._levelsList: ListCtrl = ListCtrl(self._notebook, ID_ANY, style=LC_REPORT | BORDER_SUNKEN)
        self._levelsList.SetFont(tableFont)
        self._levelsList.AppendColumn('Level', width=65)
        self._levelsList.AppendColumn('Index', width=65)
        self._levelsList.AppendColumn('Node', width=140)
        self._levelsList.AppendColumn('Type', width=80)
        self._levelsList.AppendColumn('Barycenter', width=95)
        self._notebook.AddPage(self._levelsList, 'Levels')

        # Tab 3: Links
        self._linksList: ListCtrl = ListCtrl(self._notebook, ID_ANY, style=LC_REPORT | BORDER_SUNKEN)
        self._linksList.SetFont(tableFont)
        self._linksList.AppendColumn('Source', width=110)
        self._linksList.AppendColumn('Target', width=110)
        self._linksList.AppendColumn('Hierarchical', width=100)
        self._linksList.AppendColumn('Control Pts', width=100)
        self._notebook.AddPage(self._linksList, 'Links')

    def showStep(self, snapshot: SugiyamaStepSnapshot, totalSteps: int, presetName: str):
        """
        Populate Overview, Levels, and Links tabs from a SugiyamaStepSnapshot.

        Args:
            snapshot: Active step snapshot.
            totalSteps: Total number of steps in the current preset run.
            presetName: Name of the active preset dataset.
        """
        summary: str = (
            f'Preset: {presetName}\n'
            f'Step: {snapshot.stepIndex} / {totalSteps - 1}\n'
            f'Phase: {snapshot.phaseName}\n\n'
            f'{snapshot.description}\n\n'
            f'Levels: {len(snapshot.levels)}\n'
            f'Virtual Nodes: {snapshot.virtualNodeCount}\n'
            f'Hierarchical Crossings: {snapshot.crossingCount}'
        )
        self._overviewText.SetValue(summary)

        self._levelsList.DeleteAllItems()
        levelRowIdx: int = 0
        levelRow:    List[SugiyamaNodeSnapshot]
        for levelRow in snapshot.levels:
            nodeSnap: SugiyamaNodeSnapshot
            for nodeSnap in levelRow:
                nodeType: str = 'Real'
                if nodeSnap.isVirtual:
                    nodeType = 'Virtual'
                self._levelsList.InsertItem(levelRowIdx, str(nodeSnap.level))
                self._levelsList.SetItem(levelRowIdx, 1, str(nodeSnap.index))
                self._levelsList.SetItem(levelRowIdx, 2, nodeSnap.name)
                self._levelsList.SetItem(levelRowIdx, 3, nodeType)
                self._levelsList.SetItem(levelRowIdx, 4, f'{nodeSnap.barycenter:.2f}')
                levelRowIdx += 1

        self._linksList.DeleteAllItems()
        linkRowIdx: int = 0
        linkSnap:   SugiyamaLinkSnapshot
        for linkSnap in snapshot.links:
            isHierarchicalStr: str = 'No'
            if linkSnap.isHierarchical:
                isHierarchicalStr = 'Yes'
            ptCount: int = 2
            if len(linkSnap.controlPoints) > 0:
                ptCount = len(linkSnap.controlPoints)
            self._linksList.InsertItem(linkRowIdx, linkSnap.sourceName)
            self._linksList.SetItem(linkRowIdx, 1, linkSnap.targetName)
            self._linksList.SetItem(linkRowIdx, 2, isHierarchicalStr)
            self._linksList.SetItem(linkRowIdx, 3, str(ptCount))
            linkRowIdx += 1
