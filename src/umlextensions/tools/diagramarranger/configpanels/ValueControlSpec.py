
from typing import List
from typing import NewType
from typing import Optional
from typing import Callable
from typing import TypeAlias

from enum import StrEnum

from dataclasses import dataclass

from wx import CheckBox
from wx import SpinCtrl
from wx import SpinCtrlDouble

ValueControl: TypeAlias = SpinCtrl | SpinCtrlDouble | CheckBox    # https://mypy.readthedocs.io/en/stable/common_issues.html#variables-vs-type-aliases
ValueType    = int | float | bool

MIN_VALUE:         int = 0
MAX_VALUE:         int = 10000
DEFAULT_INCREMENT: int = 1


class UnknownControlType(Exception):
    pass

class ControlType(StrEnum):
    SPIN_CTRL        = 'SpinCtrl'
    SPIN_CTRL_DOUBLE = 'SpinCtrlDouble'
    CHECK_BOX        = 'CheckBox'


@dataclass
class ValueControlSpec:

    valueLabel:       str          = ''
    valueCtrl:        ValueControl = None
    initialValue:     ValueType    = 0
    minValue:         ValueType    = MIN_VALUE
    maxValue:         ValueType    = MAX_VALUE
    spinnerIncrement: ValueType    = DEFAULT_INCREMENT
    controlType:      ControlType  = ControlType.SPIN_CTRL
    floatDigits:      int          = 2
    toolTip:          str          = ''
    textCallback:     Optional[Callable]  = None    # Not used for float spinners
    spinCallback:     Callable            = None    # type: ignore
    checkBoxCallback: Callable            = None    # type: ignore


ValueControlSpecs = NewType('ValueControlSpecs', List[ValueControlSpec])
