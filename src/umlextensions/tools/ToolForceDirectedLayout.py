
from typing import Dict
from typing import List
from typing import cast
from typing import NewType

from logging import Logger
from logging import getLogger

from wx import OK
from wx import Window
from wx import PD_APP_MODAL
from wx import ProgressDialog
from wx import PD_ELAPSED_TIME

from wx import Yield as wxYield

from pyforcedirectedlayout.LayoutTypes import LayoutStatus
from pyforcedirectedlayout.ForceDirectedLayout import ForceDirectedLayout

from umlmodel.Link import Link
from umlmodel.Link import Links
from umlmodel.Class import Class
from umlmodel.Link import LinkDestination
from umlmodel.LinkedObject import LinkedObject

from umlshapes.ShapeTypes import UmlShapes

from umlshapes.shapes.UmlClass import UmlClass
from umlshapes.links.UmlLink import UmlLink

from umlextensions.IExtensionsFacade import IExtensionsFacade

from umlextensions.extensiontypes.ExtensionDataTypes import Author
from umlextensions.extensiontypes.ExtensionDataTypes import ExtensionName
from umlextensions.extensiontypes.ExtensionDataTypes import Version

from umlextensions.tools.BaseToolExtension import BaseToolExtension
from umlextensions.tools.forcedirectedlayout.DlgConfiguration import DlgConfiguration
from umlextensions.tools.forcedirectedlayout.UmlShapeNode import UmlShapeNode

NO_PARENT_WINDOW:    Window         = cast(Window, None)
NO_PROGRESS_DIALOG:  ProgressDialog = cast(ProgressDialog, None)

NameToUmlClassMap  = NewType('NameToUmlClassMap',  Dict[str, UmlClass])
NameToUmlShapeNode = NewType('NameToUmlShapeNode', Dict[str, UmlShapeNode])


class ToolForceDirectedLayout(BaseToolExtension):

    def __init__(self, extensionsFacade: IExtensionsFacade):

        super().__init__(extensionsFacade=extensionsFacade)
        self.logger: Logger = getLogger(__name__)

        self._name    = ExtensionName('Force Directed Layout')
        self._author  = Author('Humberto A. Sanchez II')
        self._version = Version('4.0')

        self._fdl:                  ForceDirectedLayout = ForceDirectedLayout()
        self._layoutProgressDialog: ProgressDialog      = NO_PROGRESS_DIALOG
        self._nameToShapeNodeMap:   NameToUmlShapeNode = NameToUmlShapeNode({})

    def setOptions(self) -> bool:

        with DlgConfiguration(NO_PARENT_WINDOW) as dlg:
            if dlg.ShowModal() == OK:
                return True
            else:
                self.logger.warning(f'Cancelled')
                return False

    def doAction(self):
        """
        TODO:  If multiple classes share a parent or child, this can result in duplicate nodes within the
        layout engine. We need to maintain a single UmlShapeNode instance per UmlClass.
        """

        self.logger.info(f'Begin Force Directed Layout')
        selectedUmlShapes = self._frameInformation.selectedUmlShapes

        nameToClassMap: NameToUmlClassMap = self._buildNameToUmlClassMap(umlShapes=selectedUmlShapes)
        for selectedShape in selectedUmlShapes:

            if isinstance(selectedShape, UmlClass):

                umlClass:      UmlClass    = cast(UmlClass, selectedShape)      # noqa
                umlShapeNode: UmlShapeNode = UmlShapeNode(umlClass=umlClass)
                self._fdl.addNode(umlShapeNode)
                self._nameToShapeNodeMap[umlClass.modelClass.name] = umlShapeNode

                modelClass: Class = umlClass.modelClass
                self._associateChildShapeNodes(modelClass, umlShapeNode, nameToClassMap)
                self._associateShapeWithParents(modelClass, umlShapeNode, nameToClassMap)

        self._fdl.arrange(statusCallback=self._layoutStatusCallBack)
        self._reArrangeLinks(umlShapes=selectedUmlShapes)

        self._extensionsFacade.wiggleShapes()
        self.logger.info('End Force Directed Layout')

    def _associateChildShapeNodes(self, modelClass: Class, parentUmlShapeNode: UmlShapeNode, nameToUmlClassMap: NameToUmlClassMap, ):
        """
        May create shape nodes for the link destination

        Args:
            modelClass:         The model class associated with the UML Shape
            parentUmlShapeNode: The UML Shape node that may have links
            nameToUmlClassMap:  The UML Shape lookup table
        """

        links: Links = modelClass.links             # inspect the model for links

        for link in links:
            modelLink: Link = cast(Link, link)
            self.logger.info(f'{modelLink}')

            childModelClass: LinkDestination = link.destination
            childClassName:  str             = childModelClass.name

            try:
                umlChildClass:  UmlClass     = nameToUmlClassMap[childClassName]

                # Do we already have this UML Shape Node
                if childClassName in self._nameToShapeNodeMap:
                    childShapeNode: UmlShapeNode = self._nameToShapeNodeMap[childClassName]
                    self.logger.info(f'Found: {childShapeNode}')
                else:
                    childShapeNode = UmlShapeNode(umlClass=umlChildClass)
                    self._nameToShapeNodeMap[childClassName] = childShapeNode

                parentUmlShapeNode.addChild(childShapeNode)
            except KeyError:
                self.logger.warning(f'{childClassName}: not selected')

    def _associateShapeWithParents(self, modelClass: Class, umlShapeNode: UmlShapeNode, nameToUmlClassMap: NameToUmlClassMap):
        """

        Args:
            modelClass:         The model class associated with the UML Shape
            umlShapeNode:       The UML Shape node that may have parents
            nameToUmlClassMap:  The UML Shape lookup table

        """

        parents: List[LinkedObject] = modelClass.parents        # type: ignore

        for parent in parents:
            parentClassName: str = parent.name
            try:
                umlParentClass:  UmlClass     = nameToUmlClassMap[parentClassName]
                if parentClassName in self._nameToShapeNodeMap:
                    parentShapeNode: UmlShapeNode = self._nameToShapeNodeMap[parentClassName]
                    self.logger.info(f'Found: {parentShapeNode}')
                else:
                    parentShapeNode = UmlShapeNode(umlParentClass)
                    self._nameToShapeNodeMap[parentClassName] = parentShapeNode

                parentShapeNode.addChild(umlShapeNode)
            except KeyError:
                self.logger.warning(f'{parentClassName}: not selected')

    def _buildNameToUmlClassMap(self, umlShapes: UmlShapes) -> NameToUmlClassMap:
        """

        Args:
            umlShapes:   All the selected shapes on the diagram

        Returns:  An initialized name to UMLClass map

        """

        nameToUmlClassMap: NameToUmlClassMap = NameToUmlClassMap({})

        for umlShape in umlShapes:
            if isinstance(umlShape, UmlClass):

                umlClass:   UmlClass = cast(UmlClass, umlShape)     # noqa
                modelClass: Class    = umlClass.modelClass
                nameToUmlClassMap[modelClass.name] = umlClass

        return nameToUmlClassMap

    def _layoutStatusCallBack(self, status: LayoutStatus):

        # noinspection PyProtectedMember
        from wx._core import wxAssertionError

        if self._layoutProgressDialog is None:
            self._layoutProgressDialog = ProgressDialog('Arranging', 'Starting', parent=None, style=PD_APP_MODAL | PD_ELAPSED_TIME)
            self._layoutProgressDialog.SetRange(status.maxIterations)

        statusMsg: str = (
            f'totalDisplacement: {status.totalDisplacement: .3f}\n'
            f'iterations: {status.iterations}\n'
            f'stopCount: {status.stopCount}\n'
        )
        try:
            self._layoutProgressDialog.Update(status.iterations, statusMsg)
        except RuntimeError as re:
            self.logger.error(f'wxPython error: {re}')
            self._layoutProgressDialog = ProgressDialog('Arranging', 'Starting', parent=None, style=PD_APP_MODAL | PD_ELAPSED_TIME)
            self._layoutProgressDialog.SetRange(status.maxIterations)
        except wxAssertionError as ae:
            self.logger.error(f'{status.iterations=} {ae}')

        self._extensionsFacade.refreshFrame()

        wxYield()

    def _reArrangeLinks(self, umlShapes: UmlShapes):

        for umlShape in umlShapes:
            if isinstance(umlShape, UmlLink):
                umlLink: UmlLink = cast(UmlLink, umlShape)          # noqa
                self.logger.info(f"Optimizing: {umlLink}")
                umlLink.optimizeLink()
