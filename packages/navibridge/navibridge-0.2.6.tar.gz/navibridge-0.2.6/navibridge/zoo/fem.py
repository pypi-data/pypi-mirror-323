from typing import Dict

from navibridge.fem_base import Node, Element, Section, Material, Fix


class FEM:
    node_list: Dict[int, 'Node']
    elem_list: Dict[int, 'Element']
    top_elem_list: Dict[int, 'Element']
    left_elem_list: Dict[int, 'Element']
    front_elem_list: Dict[int, 'Element']
    sect_list: Dict[int, 'Section']
    mat_list: Dict[int, 'Material']
    fix_list: Dict[int, 'Fix']

    def __init__(self):
        self._initialize()

    def _initialize(self):
        """
        初始化模型。
        :return:
        """
        self.node_list: {int: Node} = {}
        self.elem_list: {int: Element} = {}
        self.top_elem_list: {int: Element} = {}
        self.left_elem_list: {int: Element} = {}
        self.front_elem_list: {int: Element} = {}
        self.sect_list: {int: Section} = {}
        self.mat_list: {int: Material} = {}
        self.fix_list: {int: Fix} = {}
        self.is_fem = False
        self.apdl = ""

    def __add__(self, other):
        if not isinstance(other, FEM):
            return NotImplemented

        # 检查重复键
        common_keys_node = self.node_list.keys() & other.node_list.keys()
        common_keys_elem = self.elem_list.keys() & other.elem_list.keys()
        common_keys_elem_t = self.top_elem_list.keys() & other.top_elem_list.keys()
        common_keys_elem_l = self.left_elem_list.keys() & other.left_elem_list.keys()
        common_keys_elem_f = self.front_elem_list.keys() & other.front_elem_list.keys()
        common_keys_sect = self.sect_list.keys() & other.sect_list.keys()
        common_keys_mat = self.mat_list.keys() & other.mat_list.keys()
        common_keys_bd = self.fix_list.keys() & other.fix_list.keys()

        if (
                common_keys_node
                or common_keys_elem
                or common_keys_elem_t
                or common_keys_elem_l
                or common_keys_elem_f
                or common_keys_sect
                or common_keys_mat
                or common_keys_bd
        ):
            raise ValueError("Cannot add FEM objects: duplicate keys found.")

        new_fem = FEM()
        new_fem.node_list = {**self.node_list, **other.node_list}
        new_fem.elem_list = {**self.elem_list, **other.elem_list}
        new_fem.top_elem_list = {**self.top_elem_list, **other.top_elem_list}
        new_fem.left_elem_list = {**self.left_elem_list, **other.left_elem_list}
        new_fem.front_elem_list = {**self.front_elem_list, **other.front_elem_list}
        new_fem.sect_list = {**self.sect_list, **other.sect_list}
        new_fem.mat_list = {**self.mat_list, **other.mat_list}
        new_fem.fix_list = {**self.fix_list, **other.fix_list}
        return new_fem

#     def __sub__(self, other):
#         if not isinstance(other, FEM):
#             return NotImplemented
#
#         new_fem = FEM()
#         new_fem.node_list = {k: v for k, v in self.node_list.items() if k not in other.node_list}
#         new_fem.elem_list = {k: v for k, v in self.elem_list.items() if k not in other.elem_list}
#         new_fem.sect_list = {k: v for k, v in self.sect_list.items() if k not in other.sect_list}
#         new_fem.mat_list = {k: v for k, v in self.mat_list.items() if k not in other.mat_list}
#         return new_fem
#
