

from typing import Union
from typing import cast

from logging import Logger
from logging import getLogger

from antlr4 import ParserRuleContext
from antlr4 import RuleContext
from antlr4.tree.Tree import TerminalNodeImpl

from codeallybasic.ConfigurationProperties import PropertyName

from umlmodel.Class import Class
from umlmodel.Field import Field
from umlmodel.FieldType import FieldType
from umlmodel.enumerations.Visibility import Visibility

from umlextensions.input.python.pythonpegparser.PythonParser import PythonParser
from umlextensions.input.python.visitor.ParserTypes import ModelClassName
from umlextensions.input.python.visitor.ParserTypes import ModelClasses

from umlextensions.input.python.pythonpegparser.PythonParserVisitor import PythonParserVisitor


NO_CLASS_DEF_CONTEXT: PythonParser.Class_defContext = cast(PythonParser.Class_defContext, None) # noqa

class BaseVisitor(PythonParserVisitor):
    def __init__(self):
        super().__init__()
        self.baseLogger: Logger = getLogger(__name__)

        self._modelClasses:  ModelClasses = ModelClasses({})

    def _isThisAssignmentInsideAMethod(self, ctx: PythonParser.AssignmentContext) -> bool:

        ans: bool = False

        currentCtx: ParserRuleContext = self._extractMethodContext(ctx=ctx)
        if currentCtx is not None:
            ans = True

        return ans

    def _makeFieldForClass(self, className: ModelClassName, propertyName: Union[PropertyName, str], typeStr: str, defaultValue: str):
        """

        Args:
            className:
            propertyName:
            typeStr:
            defaultValue:
        """
        field:      Field = Field(name=propertyName, type=FieldType(typeStr), visibility=Visibility.PUBLIC, defaultValue=defaultValue)
        modelClass: Class = self._modelClasses[className]

        modelClass.fields.append(field)

    def _extractClassName(self, ctx: PythonParser.Class_defContext) -> ModelClassName:
        """
        Get a class name from a Class_defContext
        Args:
            ctx:

        Returns:    A class name
        """

        child:     PythonParser.Class_def_rawContext = ctx.class_def_raw()
        # name:      TerminalNodeImpl                  = child.NAME()
        name:      TerminalNodeImpl = child.name()
        className: ModelClassName    = ModelClassName(name.getText())

        return className

    def _extractClassDefContext(self, ctx: ParserRuleContext) -> PythonParser.Class_defContext:
        """
        Args:
            ctx:

        Returns:  Either a class definition context or the sentinel value NO_CLASS_DEF_CONTEXT
        """
        currentCtx: RuleContext | None = ctx
        while currentCtx is not None and currentCtx.parentCtx is not None:
            if isinstance(currentCtx, PythonParser.Class_defContext):
                return currentCtx
            currentCtx = currentCtx.parentCtx

        return NO_CLASS_DEF_CONTEXT

    def _extractMethodContext(self, ctx: ParserRuleContext) -> PythonParser.Function_defContext:

        currentCtx: RuleContext | None = ctx

        while currentCtx is not None and not isinstance(currentCtx, PythonParser.Function_defContext):
            currentCtx = currentCtx.parentCtx

        if currentCtx is not None:
            raw: PythonParser.Function_def_rawContext = currentCtx.function_def_raw()
            self.baseLogger.debug(f'Found method: {raw.name()}')

        return cast(PythonParser.Function_defContext, currentCtx)

    def _findArgListContext(self, ctx: PythonParser.Class_defContext) -> PythonParser.ArgumentsContext | None:

        classDefRawContext: PythonParser.Class_def_rawContext = ctx.class_def_raw()
        argumentsCtx:       PythonParser.ArgumentsContext | None = classDefRawContext.arguments()

        return argumentsCtx
