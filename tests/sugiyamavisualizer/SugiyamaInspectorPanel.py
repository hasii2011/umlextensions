"""
Tabular inspector panel for Sugiyama layout phases, levels, and link metrics.
"""

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

from tests.sugiyamavisualizer.SugiyamaDataSet import SugiyamaDataSet
from tests.sugiyamavisualizer.SugiyamaDataSet import SugiyamaEdgeSpec

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

    def showDataSet(self, dataSet: SugiyamaDataSet):
        """
        Populate the Overview and Links tabs for the selected preset dataset.

        Args:
            dataSet: The active preset dataset.
        """
        summary: str = (
            f'Preset: {dataSet.name}\n\n'
            f'{dataSet.description}\n\n'
            f'Nodes: {len(dataSet.nodes)}\n'
            f'Edges: {len(dataSet.edges)}\n'
            f'Phase: Initial (unlaid)'
        )
        self._overviewText.SetValue(summary)

        self._levelsList.DeleteAllItems()
        self._linksList.DeleteAllItems()

        rowIndex: int = 0
        edgeSpec: SugiyamaEdgeSpec
        for edgeSpec in dataSet.edges:
            isHierarchical: str = 'Yes'
            if edgeSpec.linkType.name != 'INHERITANCE' and edgeSpec.linkType.name != 'INTERFACE':
                isHierarchical = 'No'

            self._linksList.InsertItem(rowIndex, edgeSpec.sourceName)
            self._linksList.SetItem(rowIndex, 1, edgeSpec.targetName)
            self._linksList.SetItem(rowIndex, 2, isHierarchical)
            self._linksList.SetItem(rowIndex, 3, '2')
            rowIndex += 1
