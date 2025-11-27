
from typing import List
from typing import Dict
from typing import Union
from typing import NewType

from enum import Enum

from dataclasses import dataclass

from umlmodel.Class import Class

VERSION: str = '3.0'

ModelClassName = NewType('ModelClassName', str)
ParentName     = NewType('ParentName',     str)
PropertyName   = NewType('PropertyName',   str)
ChildName      = NewType('ChildName',      str)

PropertyNames = NewType('PropertyNames', List[PropertyName])
ModelClasses  = NewType('ModelClasses',  Dict[ModelClassName, Class])

PropertyMap   = NewType('PropertyMap', Dict[ModelClassName, PropertyNames])
Children      = List[Union[ModelClassName, ChildName]]
Parents       = NewType('Parents',        Dict[ParentName,    Children])

AssociateName = ModelClassName

class AssociationType(Enum):

    ASSOCIATION = 'ASSOCIATION'
    AGGREGATION = 'AGGREGATION'
    COMPOSITION = 'COMPOSITION'
    INHERITANCE = 'INHERITANCE'
    INTERFACE   = 'INTERFACE'

@dataclass
class Associate:
    associateName:   AssociateName   = AssociateName('')
    associationType: AssociationType = AssociationType.ASSOCIATION


Associates = NewType('Associates', List[Associate])

#
# e.g.
#     @property
#     def pages(self) -> Pages:
#         return self._pages
# In the above "Pages" is the AssociateName and goes in the List for the method containing ModelClassName
#
# e.g.
#  self.pages: Pages = Pages({})
#
#  Pages is the AssociateName and the enclosing class for the __init__ method is the ModelClassName
#
#
Associations = NewType('Associations', Dict[ModelClassName, Associates])
