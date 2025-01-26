from typing import Union

from .fem import FEM
from ..fem_base import Material
from ..fem_base.section import Section


class SectionGroup(FEM):
    def __init__(self):
        super().__init__()

    def add(self, obj: Union[Section, Material]):
        if isinstance(obj, Section):
            self.sect_list[obj.id] = obj
        elif isinstance(obj, Material):
            self.mat_list[obj.id] = obj
        else:
            raise TypeError
