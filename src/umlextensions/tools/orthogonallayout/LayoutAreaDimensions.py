
from typing import List

from dataclasses import dataclass


@dataclass
class LayoutAreaDimensions:

    width:  int = 0
    height: int = 0

    @classmethod
    def deSerialize(cls, value: str) -> 'LayoutAreaDimensions':

        layoutAreaSize: LayoutAreaDimensions = LayoutAreaDimensions()

        widthHeight: List[str] = value.split(sep=',')

        if len(widthHeight) != 2:
            raise ValueError(f'Incorrectly formatted dimensions: {value}')

        if not value.replace(',', '', 1).isdigit():
            raise ValueError(f'String must be numeric: {value}')

        layoutAreaSize.width  = int(widthHeight[0])
        layoutAreaSize.height = int(widthHeight[1])

        return layoutAreaSize

    def __str__(self):
        return f'{self.width},{self.height}'

    def __repr__(self):
        return self.__str__()
