from typing import Tuple, List

import numpy as np

from . import Node
from .base import ApdlWriteable


class Element(ApdlWriteable):
    __slots__ = ('e', 'nlist', 'mat', 'etype', 'real', 'secn', '_npts')

    nlist: List[Node]

    def __init__(self, e: int, mat: int, secn: int, nodes: List[Node], etype: int = 188, real: int = 188):
        self.id = e
        self.mat = mat
        self.etype = etype
        self.real = real
        self.secn = secn
        self._npts = len(nodes)
        if self.etype == 188:
            if len(nodes) != 2:
                raise Exception("BEAM188应使用2个Node.")
            else:
                self.nlist = nodes
        elif etype == 181 or etype == 182:
            if len(nodes) != 4:
                raise Exception("SHELL181应使用4个Node.")
            else:
                self.nlist = nodes
        elif etype == 1841 or etype == 1840:
            if len(nodes) != 2:
                raise Exception("MPC184应使用2个Node.")
            else:
                self.nlist = nodes
        else:
            raise Exception("单元类型不支持.")

    @property
    def location(self):
        x0 = np.mean([n.x for n in self.nlist])
        y0 = np.mean([n.y for n in self.nlist])
        z0 = np.mean([n.z for n in self.nlist])
        return x0, y0, z0

    @property
    def apdl_str(self):
        cmd_str = '''mat,%i
type,%i
real,%i
secn,%i
e,''' % (self.mat, self.etype, self.real, self.secn)
        for nn in self.nlist:
            cmd_str += "%i" % nn.id
            cmd_str += ','
        # cmd_str += '9999999'
        return cmd_str

    def __str__(self):
        ss = "Elem: (%i,type=%i,secn=%i,nlist=[" % (self.e, self.etype, self.secn,)
        for n in self.nlist:
            ss += "%i," % n.id
        ss += "])"
        return ss
