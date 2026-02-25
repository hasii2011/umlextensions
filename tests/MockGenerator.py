
from typing import List

from logging import Logger
from logging import getLogger

from unittest.mock import MagicMock
from unittest.mock import PropertyMock

from umlmodel.Class import Class
from umlmodel.Link import Link
from umlmodel.enumerations.LinkType import LinkType
from umlmodel.enumerations.Stereotype import Stereotype

from umlshapes.links.UmlLink import UmlLink
from umlshapes.shapes.UmlClass import UmlClass
from umlshapes.types.UmlPosition import UmlPosition

from umlshapes.types.Common import EndPositions
from umlshapes.types.UmlDimensions import UmlDimensions
from umlshapes.types.UmlPosition import UmlPositions


class MockGenerator:
    NUMBER_OF_MOCK_CLASSES:    int = 2
    MOCK_CLASS_NAME_PREFIX:    str = 'ClassName_'

    MOCK_ID_NUMBER_INCREMENT:  int = 5
    MOCK_INIT_WIDTH:           int = 50
    MOCK_INIT_HEIGHT:          int = 50
    MOCK_INIT_POSITION_X:      int = 100
    MOCK_INIT_POSITION_Y:      int = 100
    MOCK_X_POSITION_INCREMENT: int = 75
    MOCK_Y_POSITION_INCREMENT: int = 100

    def __init__(self, mockClassNamePrefix: str = MOCK_CLASS_NAME_PREFIX):

        self.logger: Logger = getLogger(__name__)

        self._mockClassNamePrefix: str = mockClassNamePrefix

        self._classIdGenerator = self._generateClassId()
        self._linkIDGenerator  = self._generateLinkId()

    def generateMockNodes(self, nbrToGenerate) -> List[MagicMock]:

        umlShapes: List[MagicMock] = []

        mockX: int = MockGenerator.MOCK_INIT_POSITION_X
        mockY: int = MockGenerator.MOCK_INIT_POSITION_Y
        mockWidth:  int = MockGenerator.MOCK_INIT_WIDTH
        mockHeight: int = MockGenerator.MOCK_INIT_HEIGHT

        for x in range(nbrToGenerate):

            classId:        str   = next(self._classIdGenerator)
            mockModelClass: Class = self._createMockModelClass(classId)

            mockUmlClass: MagicMock                = MagicMock(spec=UmlClass)
            # mockOglClass.GetPosition.return_value  = (mockX, mockY)
            # mockOglClass.GetSize.return_value      = (mockWidth, mockHeight)
            type(mockUmlClass).position    = PropertyMock(return_value=UmlPosition(x=mockX, y=mockY))
            type(mockUmlClass).size        = PropertyMock(return_value=UmlDimensions(width=mockWidth, height=mockHeight))
            type(mockUmlClass).id          = PropertyMock(return_value=classId)
            type(mockUmlClass).modelClass  = PropertyMock(return_value=mockModelClass)

            umlShapes.append(mockUmlClass)

            mockX  += MockGenerator.MOCK_X_POSITION_INCREMENT
            mockY  += MockGenerator.MOCK_Y_POSITION_INCREMENT

        return umlShapes

    def addMockLinks(self, umlShapes: List[MagicMock]):

        currentIdx: int = 0
        while True:

            parentClass: MagicMock = umlShapes[currentIdx]
            childClass:  MagicMock = umlShapes[currentIdx + 1]

            self.logger.info(f'parentID: {parentClass.id} childID: {childClass.id}')
            self._createMockLink(parentClass, childClass)
            currentIdx += 2
            if currentIdx >= len(umlShapes):
                break

    def _createMockModelClass(self, classNumber: str) -> MagicMock:
        """

        Args:
            classNumber:
        Returns:
        """
        mockModelClass: MagicMock = MagicMock(spec=Class)
        className: str = f'{MockGenerator.MOCK_CLASS_NAME_PREFIX}{classNumber}'
        # mockPyutClass.getName.return_value = className

        type(mockModelClass).name = PropertyMock(return_value=className)
        type(mockModelClass).stereotype = Stereotype.TYPE

        return mockModelClass

    def _createMockLink(self, src: MagicMock, dst: MagicMock) -> MagicMock:
        """
        Args:
            src:   Mock UmlClass
            dst:   Mock UmlClass

        Returns:
            Mocked UmlLink
        """
        umlLink:  MagicMock = MagicMock(spec=UmlLink)

        linkId: str = next(self._linkIDGenerator)

        type(umlLink).id = PropertyMock(return_value=linkId)

        # mockSourceAnchor:      MagicMock = MagicMock(spec=AnchorPoint)
        # mockDestinationAnchor: MagicMock = MagicMock(spec=AnchorPoint)

        # mockSourceAnchor.GetPosition.return_value      = [22, 44]
        # mockDestinationAnchor.GetPosition.return_value = [1024, 450]

        # umlLink.endPoints = EndPoints(
        #     toPosition=umlLinkAttributes.toPosition,
        #     fromPosition=umlLinkAttributes.fromPosition
        # )

        endPositions: EndPositions = EndPositions(
            fromPosition=UmlPosition(x=22, y=44),
            toPosition=UmlPosition(x=1024, y=450),
        )
        type(umlLink).endPositions = PropertyMock(return_value=endPositions)

        # mockLinePointMiddle: MagicMock = MagicMock(spec=LinePoint)
        mockPositionMiddle: UmlPosition = UmlPosition(x=100, y=100)

        type(umlLink).controlPositions  = PropertyMock(return_value=UmlPositions([mockPositionMiddle]))
        # type(oglLink).sourceAnchor      = PropertyMock(return_value=mockSourceAnchor)
        # type(oglLink).destinationAnchor = PropertyMock(return_value=mockDestinationAnchor)

        type(umlLink).sourceShape      = PropertyMock(return_value=src)
        type(umlLink).destinationShape = PropertyMock(return_value=dst)
        #
        # PyutLink object simple enough so create real one
        # pyutLink: PyutLink = PyutLink("", linkType=PyutLinkType.INHERITANCE, source=src.pyutObject, destination=dst.pyutObject)
        link: Link = Link(name='', linkType=LinkType.INHERITANCE, source=src.modelClass, destination=dst.modelClass)
        type(src).links = PropertyMock(return_value=[umlLink])
        type(dst).links = PropertyMock(return_value=[umlLink])

        mockPyutClass = src.modelClass
        type(mockPyutClass).links = PropertyMock(return_value=[link])

        return umlLink

    def _generateClassId(self):
        classId: int = 10000
        while True:
            yield str(classId)
            classId += 10

    def _generateLinkId(self):
        linkId: int = 1024
        while True:
            yield str(linkId)
            linkId += 1
