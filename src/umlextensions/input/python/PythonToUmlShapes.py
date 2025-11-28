
from typing import Union
from typing import cast
from typing import Dict
from typing import List
from typing import NewType
from typing import Callable

from logging import Logger
from logging import getLogger

from os import sep as osSep
from os import linesep as osLineSep

from antlr4 import CommonTokenStream
from antlr4 import FileStream
from antlr4.error.ErrorListener import ErrorListener

from umlmodel.Class import Class
from umlmodel.Link import Link
from umlmodel.enumerations.LinkType import LinkType

from wx import OK
from wx import ICON_ERROR
from wx import ICON_WARNING

from wx import MessageBox

from umlshapes.frames.ClassDiagramFrame import ClassDiagramFrame

from umlshapes.links.eventhandlers.UmlLinkEventHandler import UmlLinkEventHandler
from umlshapes.links.eventhandlers.UmlAssociationEventHandler import UmlAssociationEventHandler

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

from umlshapes.shapes.eventhandlers.UmlClassEventHandler import UmlClassEventHandler

from umlshapes.shapes.UmlClass import UmlClass

from umlshapes.links.UmlAggregation import UmlAggregation
from umlshapes.links.UmlAssociation import UmlAssociation
from umlshapes.links.UmlComposition import UmlComposition
from umlshapes.links.UmlInheritance import UmlInheritance

from umlshapes.ShapeTypes import UmlAssociationGenre
from umlshapes.ShapeTypes import UmlShapes
from umlshapes.ShapeTypes import UmlLinks

from umlextensions.input.python.PythonParseException import PythonParseException

from umlextensions.input.python.pythonpegparser.PythonLexer import PythonLexer
from umlextensions.input.python.pythonpegparser.PythonParser import PythonParser

from umlextensions.input.python.visitor.ParserTypes import Associate
from umlextensions.input.python.visitor.ParserTypes import Associates
from umlextensions.input.python.visitor.ParserTypes import AssociationType
from umlextensions.input.python.visitor.ParserTypes import Associations
from umlextensions.input.python.visitor.ParserTypes import Children

from umlextensions.input.python.visitor.ParserTypes import Parents
from umlextensions.input.python.visitor.ParserTypes import ChildName
from umlextensions.input.python.visitor.ParserTypes import ParentName
from umlextensions.input.python.visitor.ParserTypes import ModelClasses
from umlextensions.input.python.visitor.ParserTypes import ModelClassName

from umlextensions.input.python.visitor.PythonPegParserClassVisitor import PythonPegParserClassVisitor
from umlextensions.input.python.visitor.PythonPegParserVisitor import PythonPegParserVisitor

ProgressCallback = Callable[[int, str], None]

UmlClassesDict = NewType('UmlClassesDict', Dict[Union[ModelClassName, ParentName, ChildName], UmlClass])


class PythonErrorListener(ErrorListener):
    #
    # Provides a default instance of {@link ConsoleErrorListener}.
    #
    # INSTANCE = None

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):

        # print("line " + str(line) + ":" + str(column) + " " + msg, file=sys.stderr)
        eMsg: str = f'{line=}{osLineSep}{column=}{osLineSep}{msg}'
        raise PythonParseException(eMsg)

class PythonToUmlShapes:
    """
    I wanted to only create 'bare' UML Classes and UML Links.  But, by virtue of how
    the OGL layer works, I have to fully prepare the shapes.  Thus, it is necessary
    for me to inject the UI frames and the pub sub engines into all the created shapes.

    """
    def __init__(self, classDiagramFrame: ClassDiagramFrame, umlPubSubEngine: IUmlPubSubEngine):

        self._classDiagramFrame: ClassDiagramFrame = classDiagramFrame
        self._umlPubSubEngine:   IUmlPubSubEngine  = umlPubSubEngine

        self.logger: Logger = getLogger(__name__)

        self._umlClasses: UmlShapes = UmlShapes([])
        self._umlLinks:   UmlLinks  = UmlLinks([])

        self._cumulativeParents: Parents = Parents({})
        """
        This dictionary is keyed by a class name that is the base class of at least one subclass.  The
        subclass value is a list of subclasses
        """
        self._cumulativeAssociations: Associations = Associations({})

    @property
    def umlLinks(self) -> UmlLinks:
        """
        Not valid until the call to .generateLinks

        Returns:
        """
        return self._umlLinks

    def pass1(self, directoryName: str, files: List[str], progressCallback: ProgressCallback) -> ModelClasses:
        """
        Uses the simplified class visitor

        Args:
            directoryName:    The fully qualified directory name of the python files
            files:            The list of files to parse
            progressCallback: A callback to report status as each file is processed; The callback
            should have the signature of the type ProgressCallback

        Returns:  The Python code parsed into model classes
        """
        modelClasses:      ModelClasses = ModelClasses({})
        currentFileCount: int         = 0

        for fileName in files:
            try:
                fqFileName: str = f'{directoryName}{osSep}{fileName}'
                self.logger.info(f'1st pass Processing file: {fqFileName}')

                progressCallback(currentFileCount, f'Pass 1 processing: {directoryName}\n {fileName}')

                tree:    PythonParser.File_inputContext = self._setupPegBasedParser(fqFileName=fqFileName)
                visitor: PythonPegParserClassVisitor    = PythonPegParserClassVisitor()

                visitor.modelClasses = modelClasses
                visitor.visit(tree)
                modelClasses = visitor.modelClasses

            except (ValueError, Exception, PythonParseException) as e:
                if isinstance(e, PythonParseException):
                    errorMsg: str = f'{fileName}\n{e}'
                    self.logger.error(e)
                    MessageBox(errorMsg, 'Error', OK | ICON_ERROR)
                else:
                    self.logger.error(f'Error in {directoryName}/{fileName}')
                    raise e

            if len(modelClasses) == 0:
                MessageBox('No classes processed', 'Warning', OK | ICON_WARNING)

        return modelClasses

    def pass2(self, directoryName: str, files: List[str], modelClasses: ModelClasses, progressCallback: Callable) -> ModelClasses:
        """
        Reverse engineering Python files to UMl Shapes

        Uses the full Python Peg Parser Visitor

        Args:
            directoryName:    The fully qualified directory name where the selected files reside
            files:            A list of files to parse
            modelClasses:     The full list of classes scanned during pass 1
            progressCallback: The method to call to report progress
        """
        currentFileCount: int = 0
        for fileName in files:

            try:
                fqFileName: str = f'{directoryName}{osSep}{fileName}'
                self.logger.info(f'2nd pass processing file: {fqFileName}')

                progressCallback(currentFileCount, f'2nd pass - processing: {directoryName}\n {fileName}')

                tree: PythonParser.File_inputContext = self._setupPegBasedParser(fqFileName=fqFileName)
                #
                # Account for empty files
                #
                if tree is None:
                    continue

                visitor: PythonPegParserVisitor = PythonPegParserVisitor()
                #
                # Re-Initialize the visitor for this pass
                #
                visitor.modelClasses  = modelClasses
                visitor.parents      = self._cumulativeParents
                visitor.associations = self._cumulativeAssociations
                visitor.visit(tree)

                # Save the updated parents and associations
                self._cumulativeParents      = visitor.parents
                self._cumulativeAssociations = visitor.associations

            except (ValueError, Exception, PythonParseException) as e:
                if isinstance(e, PythonParseException):
                    errorMsg: str = f'{fileName}\n{e}'
                    self.logger.error(e)
                    MessageBox(errorMsg, 'Error', OK | ICON_ERROR)
                else:
                    raise e

        return modelClasses

    def generateUmlClasses(self, modelClasses: ModelClasses) -> UmlClassesDict:

        umlClassesDict: UmlClassesDict = UmlClassesDict({})
        for modelClassName in modelClasses:
            try:
                modelClass: Class    = modelClasses[modelClassName]
                umlClass:   UmlClass = UmlClass(modelClass=modelClass)

                eventHandler: UmlClassEventHandler = UmlClassEventHandler()
                eventHandler.SetShape(umlClass)
                eventHandler.SetPreviousHandler(umlClass.GetEventHandler())

                umlClass.SetEventHandler(eventHandler)
                umlClass.umlFrame = self._classDiagramFrame

                eventHandler.umlPubSubEngine = self._umlPubSubEngine

                umlClassesDict[ModelClassName(modelClassName)] = umlClass

            except (ValueError, Exception) as e:
                self.logger.error(f"Error while creating class {modelClassName},  {e}")

        return umlClassesDict

    def generateLinks(self, umlClassesDict: UmlClassesDict):
        self._generateInheritanceLinks(umlClassesDict)
        self._generateAssociationLinks(umlClassesDict)

    def _generateInheritanceLinks(self, umlClassesDict: UmlClassesDict):
        """
        Creates UML Inheritance links
        Args:
            umlClassesDict:

        """
        parents: Parents = self._cumulativeParents

        for parentName in parents.keys():
            children: Children = parents[parentName]

            for childName in children:

                try:
                    baseClass: UmlClass = umlClassesDict[parentName]
                    subClass:  UmlClass = umlClassesDict[childName]

                    umlInheritance: UmlInheritance = self._createInheritanceLink(subClass=subClass, baseClass=baseClass)

                    self._umlLinks.append(umlInheritance)
                except KeyError as ke:  # Probably there is no parent we are tracking
                    self.logger.warning(f'Apparently we are not tracking this parent:  {ke}')
                    continue

    def _generateAssociationLinks(self, umlClassesDict: UmlClassesDict):

        associations: Associations = self._cumulativeAssociations

        for className in associations:
            modelClassName: ModelClassName = cast(ModelClassName, className)
            associates:     Associates    = associations[modelClassName]

            for assoc in associates:
                associate: Associate = cast(Associate, assoc)
                sourceClass:      UmlClass = umlClassesDict[modelClassName]
                destinationClass: UmlClass = umlClassesDict[associate.associateName]

                linkType: LinkType   = self._toLinkType(associationType=associate.associationType)
                oglLink: UmlAssociationGenre = self._createAssociationLink(sourceClass=sourceClass, destinationClass=destinationClass, linkType=linkType)

                self._umlLinks.append(oglLink)

    def _setupPegBasedParser(self, fqFileName: str) -> PythonParser.File_inputContext:
        """
        May return None if there are syntax errors in the input file
        In that case the error listener will raise and PythonParseException exception
        with the appropriate detailed error message

        Args:
            fqFileName:

        Returns:  Returns a visitor
        """

        fileStream: FileStream  = FileStream(fqFileName)
        lexer:      PythonLexer = PythonLexer(fileStream)

        stream: CommonTokenStream = CommonTokenStream(lexer)
        parser: PythonParser      = PythonParser(stream)

        parser.removeParseListeners()
        parser.addErrorListener(PythonErrorListener())

        tree: PythonParser.File_inputContext = parser.file_input()
        if parser.getNumberOfSyntaxErrors() != 0:
            eMsg: str = f"File {fqFileName} contains {parser.getNumberOfSyntaxErrors()} syntax errors"
            self.logger.error(eMsg)
            tree = cast(PythonParser.File_inputContext, None)

        return tree

    def _createInheritanceLink(self, subClass: UmlClass, baseClass: UmlClass) -> UmlInheritance:

        link: Link = Link("", linkType=LinkType.INHERITANCE,
                          source=subClass.modelClass,
                          destination=baseClass.modelClass
                          )

        umlInheritance: UmlInheritance = UmlInheritance(link=link, baseClass=baseClass, subClass=subClass)

        umlInheritance.umlFrame = self._classDiagramFrame
        umlInheritance.MakeLineControlPoints(n=2)       # Make this configurable

        # REMEMBER:   from subclass to base class
        subClass.addLink(umlLink=umlInheritance, destinationClass=baseClass)

        eventHandler: UmlLinkEventHandler = UmlLinkEventHandler(umlLink=umlInheritance)
        eventHandler.umlPubSubEngine = self._umlPubSubEngine
        eventHandler.SetShape(umlInheritance)
        eventHandler.SetPreviousHandler(umlInheritance.GetEventHandler())
        umlInheritance.SetEventHandler(eventHandler)

        eventHandler.umlPubSubEngine = self._umlPubSubEngine

        return umlInheritance

    def _createAssociationLink(self, sourceClass: UmlClass, destinationClass: UmlClass, linkType: LinkType) -> UmlAssociationGenre:

        link: Link = self._createAssociationModelLink(linkType=linkType,
                                                      sourceClass=sourceClass.modelClass,
                                                      destinationClass=destinationClass.modelClass
                                                      )
        umlAssociation: UmlAssociationGenre

        if linkType == LinkType.ASSOCIATION:
            umlAssociation = UmlAssociation(link=link)
        elif linkType == LinkType.AGGREGATION:
            umlAssociation = UmlAggregation(link=link)
        elif linkType == LinkType.COMPOSITION:
            umlAssociation = UmlComposition(link=link)
        else:
            assert False, 'Unknown association type'

        umlAssociation.umlFrame = self._classDiagramFrame
        umlAssociation.umlPubSubEngine = self._umlPubSubEngine
        umlAssociation.MakeLineControlPoints(n=2)       # Make this configurable

        sourceClass.addLink(umlLink=umlAssociation, destinationClass=destinationClass)

        eventHandler: UmlAssociationEventHandler = UmlAssociationEventHandler(umlAssociation=umlAssociation)
        eventHandler.umlPubSubEngine = self._umlPubSubEngine
        eventHandler.SetShape(umlAssociation)
        eventHandler.SetPreviousHandler(umlAssociation.GetEventHandler())
        umlAssociation.SetEventHandler(eventHandler)

        eventHandler.umlPubSubEngine = self._umlPubSubEngine

        return umlAssociation

    # noinspection PyUnboundLocalVariable
    def _toLinkType(self, associationType: AssociationType) -> LinkType:

        match associationType:
            case AssociationType.ASSOCIATION:
                linkType: LinkType = LinkType.ASSOCIATION
            case AssociationType.AGGREGATION:
                linkType = LinkType.AGGREGATION
            case AssociationType.COMPOSITION:
                linkType = LinkType.COMPOSITION
            case _:
                assert False, f'Unknown association type: {associationType.name}'

        return linkType

    def _createAssociationModelLink(self, sourceClass: Class, destinationClass: Class, linkType: LinkType) -> Link:
        """
        Creates a model link based on the model classes and the link type
        Args:
            sourceClass:
            destinationClass:
            linkType:

        Returns:  A model link
        """

        name: str = f' Association '
        link: Link = Link(name=name, source=sourceClass, destination=destinationClass, linkType=linkType)

        link.sourceCardinality      = 'source Cardinality'
        link.destinationCardinality = 'destination Cardinality'

        return link
