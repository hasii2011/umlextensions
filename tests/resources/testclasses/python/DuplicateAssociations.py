from dataclasses import dataclass
from enum import Enum


class DisplayMethods(Enum):
    UNSPECIFIED = 'UNSPECIFIED'
    DISPLAY     = 'DISPLAY'


class DisplayParameters(Enum):
    UNSPECIFIED = 'UNSPECIFIED'
    DISPLAY     = 'DISPLAY'


@dataclass
class TargetClass:
    displayParameters:    DisplayParameters = DisplayParameters.UNSPECIFIED
    displayConstructor:   DisplayMethods    = DisplayMethods.UNSPECIFIED
    displayDunderMethods: DisplayMethods    = DisplayMethods.UNSPECIFIED
