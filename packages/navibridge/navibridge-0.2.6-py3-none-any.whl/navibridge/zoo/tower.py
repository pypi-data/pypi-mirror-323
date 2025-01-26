from typing import List

import pint
from PyAngle import Angle
from ezdxf.math import Vec3
from scipy.optimize import bisect

from .fem import FEM
from ..fem_base import Node, Element, Fix

ureg = pint.UnitRegistry()
Q_ = ureg.Quantity


def cal_angle(fw, fl, zup, zlow):
    pts_up = [
        Vec3(+fl(zup) * 0.5, +fw(zup) * 0.5, zup),
        Vec3(-fl(zup) * 0.5, +fw(zup) * 0.5, zup),
        Vec3(+fl(zup) * 0.5, -fw(zup) * 0.5, zup),
    ]
    pts_low = [
        Vec3(+fl(zlow) * 0.5, +fw(zlow) * 0.5, zlow),
        Vec3(-fl(zlow) * 0.5, +fw(zlow) * 0.5, zlow),
        Vec3(+fl(zlow) * 0.5, -fw(zlow) * 0.5, zlow),
    ]
    O = pts_low[0]
    M = pts_up[0]
    A = (M + pts_up[1]) * 0.5
    B = (M + pts_up[2]) * 0.5
    a = Angle.from_rad((M - O).angle_between((A - O))).to_degrees()
    b = Angle.from_rad((M - O).angle_between((B - O))).to_degrees()
    return min(a, b)


def target_func(deltaX, x0, fw, fl, ang):
    return cal_angle(fw, fl, x0, x0 - deltaX) - ang


def create_dist_list(fw, fl, height, ang):
    ret = [0]
    while sum(ret) < height:
        z0 = -sum(ret)
        r = bisect(target_func, 100, 20000, args=(z0 * 1000, fw, fl, ang))
        int_part = int(r / 500)
        ret.append(int_part * 500 * 1e-3)
    ret.remove(ret[0])
    return ret


def easy_tower(tower_id, cc, height, ref_ground, l_fun, w_fun, delta_h, delta_l, s, targe_ang=30.0):
    dist = create_dist_list(w_fun, l_fun, height, targe_ang)
    fem_list = []
    for i, d in enumerate(dist):
        z0 = -sum(dist[0:i]) * 1000
        z1 = z0 - d * 1000
        width0 = w_fun(z0)
        length0 = l_fun(z0)
        width1 = w_fun(z1)
        length1 = l_fun(z1)
        cc0 = cc + Vec3(0, 0, z0)
        if i == (len(dist) - 1):
            add_fix = True
        else:
            add_fix = False
        if i == 0:
            add_top = True
        else:
            add_top = False
        if d >= 15:
            layerN = 3
        elif d >= 7.5:
            layerN = 2
        else:
            layerN = 1
        for px, xi in enumerate([-1, 1]):
            for py, yi in enumerate([-1, 1]):
                bi = f"{px:01b}{py:01b}"
                dec = int(bi, 2) + 1
                if tower_id % 2 == 0:
                    dec += 5
                basen = int(((tower_id - 1) // 2 + 1) * 1e5 + dec * 1e4 + (i + 1) * 1e2)
                md = TriTower(width0, length0, width1, length1, d * 1000, cc0, basen,
                              xi, yi, layerN, ref_ground, [1, 2, 3, 4], slope=s, delt_H=delta_h, delt_L=delta_l,
                              add_fix=add_fix, add_top_brace=add_top)
                fem_list.append(md)
    return sum(fem_list, FEM())


class TriTower(FEM):
    def __init__(self, W0, L0, W1, L1, H, center: Vec3, base_n: int, xdir: int, ydir: int, layer: int,
                 ground_level: float, sect_list, slope,
                 delt_H: float, delt_L: float, add_top_brace=False, add_fix=False):
        """
        生成塔节段
        """
        super().__init__()
        self.H = H
        self.ground_e = ground_level
        self.base_n = base_n
        self.cc = center
        self.xdir = xdir
        self.ydir = ydir
        self.pO = center + Vec3(xdir * 0.5 * L1, ydir * 0.5 * W1, -H)
        self.pA = center + Vec3(xdir * 0.5 * L0, ydir * 0.5 * W0, 0)
        self.pB = center + Vec3(xdir * 0.5 * L0, 0, 0)
        self.pC = center + Vec3(0, ydir * 0.5 * W0, 0)
        self.pD = center + Vec3(xdir * 0.5 * L0, ydir * 0.5 * W0, delt_H - xdir * 0.5 * L0 * (abs(slope)))
        self.pE = center + Vec3(xdir * (0.5 * L0 + delt_L), ydir * 0.5 * W0, delt_H + xdir * (0.5 * L0 + delt_L) * (-(abs(slope))))
        self.OA = (self.pA - self.pO)
        self.OB = (self.pB - self.pO)
        self.OC = (self.pC - self.pO)
        self.AB = (self.pB - self.pA)
        self.AC = (self.pC - self.pA)
        self.layer = layer
        self.e2windx = []
        self.e2windy = []
        self.slist = sect_list
        # self.add_top_brace = add_top_brace
        self.tri_gen(add_fix, add_top_brace)

    def tri_gen(self, is_fix: bool, add_top_brace: bool):
        main_tube_secn = self.slist[0]
        dia_tube_secn = self.slist[1:]
        others = 9
        eid = 0
        killerAB = (self.OA - self.OB).magnitude > 3 * (self.OA.magnitude / self.layer)
        killerAC = (self.OA - self.OC).magnitude > 3 * (self.OA.magnitude / self.layer)
        # OAC
        for n in range(self.layer + 1):
            if n == 0:
                self.add(Node(self.base_n + 1, self.pO))
                if is_fix:
                    self.fix_list[self.base_n + 1] = Fix(self.base_n + 1, {'all': 0})
            else:
                self.add(Node(self.base_n + 1 + n * 10, self.pO + self.OA * (n / self.layer)))
                self.add(Node(self.base_n + 2 + n * 10, self.pO + self.OB * (n / self.layer)))
                self.add(Node(self.base_n + 3 + n * 10, self.pO + self.OC * (n / self.layer)))
                if n == 1:
                    eid = self.quick_elem([11, 1], self.base_n + 1 + n * 10, main_tube_secn, 1)
                    # if self.ydir > 0:
                    #     self.e2windy.append(self.get_e_loc(self.base_n + 1 + n * 10))
                    # if self.xdir > 0:
                    #     self.e2windx.append(self.get_e_loc(self.base_n + 1 + n * 10))
                    eid = self.quick_elem([12, 1], eid, dia_tube_secn[0], 1)
                    eid = self.quick_elem([13, 1], eid, dia_tube_secn[0], 1)
                else:
                    eid = self.quick_elem([1 + n * 10, 1 + (n - 1) * 10], eid, main_tube_secn, 1)
                    # if self.ydir > 0:
                    #     self.e2windy.append(self.get_e_loc(eid - 1))
                    # if self.xdir > 0:
                    #     self.e2windx.append(self.get_e_loc(eid - 1))
                    eid = self.quick_elem([2 + n * 10, 2 + (n - 1) * 10], eid, dia_tube_secn[0], 2)
                    eid = self.quick_elem([3 + n * 10, 3 + (n - 1) * 10], eid, dia_tube_secn[0], 2)
                if (n + 1) / (self.layer + 1) > 2 / 3:
                    if killerAB and killerAC:
                        curA = self.pO + self.OA * (n / self.layer)
                        curB = self.pO + self.OB * (n / self.layer)
                        curC = self.pO + self.OC * (n / self.layer)
                        self.add(Node(self.base_n + 4 + n * 10, curB - 0.5 * self.AB))
                        self.add(Node(self.base_n + 5 + n * 10, curB + 0.5 * (curC - curB)))
                        self.add(Node(self.base_n + 6 + n * 10, curC - 0.5 * self.AC))
                        eid = self.quick_elem(
                            [1 + n * 10, 4 + n * 10, 2 + n * 10, 5 + n * 10, 3 + n * 10, 6 + n * 10, ],
                            eid, others, 2, True)
                        eid = self.quick_elem([4 + n * 10, 5 + n * 10, 6 + n * 10, ], eid, others, 2, True)
                        if self.node_list.keys().__contains__(self.base_n + (n - 1) * 10 + 4):
                            eid = self.quick_elem([2 + (n - 1) * 10, 4 + n * 10, 4 + (n - 1) * 10, 1 + n * 10, ], eid,
                                                  others, 2)
                            eid = self.quick_elem([3 + (n - 1) * 10, 6 + n * 10, 6 + (n - 1) * 10, 1 + n * 10, ], eid,
                                                  others, 2)
                        else:
                            eid = self.quick_elem([2 + (n - 1) * 10, 4 + n * 10, 1 + (n - 1) * 10, ], eid, others, 2)
                            eid = self.quick_elem([3 + (n - 1) * 10, 6 + n * 10, 1 + (n - 1) * 10, ], eid, others, 2)
                    elif killerAB:
                        curA = self.pO + self.OA * (n / self.layer)
                        curB = self.pO + self.OB * (n / self.layer)
                        curC = self.pO + self.OC * (n / self.layer)
                        self.add(Node(self.base_n + 4 + n * 10, curB - 0.5 * self.AB))
                        self.add(Node(self.base_n + 5 + n * 10, curB + 0.5 * (curC - curB)))
                        eid = self.quick_elem([1 + n * 10, 4 + n * 10, 2 + n * 10, 5 + n * 10, 3 + n * 10, ],
                                              eid, others, 2, True)
                        eid = self.quick_elem([4 + n * 10, 5 + n * 10, 1 + n * 10], eid, others, 2)
                        if self.node_list.keys().__contains__(self.base_n + (n - 1) * 10 + 4):
                            eid = self.quick_elem([2 + (n - 1) * 10, 4 + n * 10, 4 + (n - 1) * 10, 1 + n * 10, ], eid,
                                                  others, 2)
                        else:
                            eid = self.quick_elem([2 + (n - 1) * 10, 4 + n * 10, 1 + (n - 1) * 10, ], eid, others, 2)
                        eid = self.quick_elem([1 + n * 10, 3 + (n - 1) * 10], eid, others, 2)
                    elif killerAC:
                        curA = self.pO + self.OA * (n / self.layer)
                        curB = self.pO + self.OB * (n / self.layer)
                        curC = self.pO + self.OC * (n / self.layer)
                        self.add(Node(self.base_n + 5 + n * 10, curB + 0.5 * (curC - curB)))
                        self.add(Node(self.base_n + 6 + n * 10, curC - 0.5 * self.AC))
                        eid = self.quick_elem([1 + n * 10, 2 + n * 10, 5 + n * 10, 3 + n * 10, 6 + n * 10, ],
                                              eid, others, 2, True)
                        eid = self.quick_elem([1 + n * 10, 5 + n * 10, 6 + n * 10, ], eid, others, 2)
                        if self.node_list.keys().__contains__(self.base_n + (n - 1) * 10 + 6):
                            eid = self.quick_elem([3 + (n - 1) * 10, 6 + n * 10, 6 + (n - 1) * 10, 1 + n * 10, ], eid,
                                                  others, 2)
                        else:
                            eid = self.quick_elem([3 + (n - 1) * 10, 6 + n * 10, 1 + (n - 1) * 10, ], eid, others, 2)
                        eid = self.quick_elem([1 + n * 10, 2 + (n - 1) * 10], eid, others, 2)
                    else:
                        if n == self.layer:
                            eid = self.quick_elem([2 + n * 10, 1 + n * 10, 3 + n * 10], eid, dia_tube_secn[1], 2)  # 顶层三角
                            eid = self.quick_elem([2 + n * 10, 3 + n * 10], eid, dia_tube_secn[2], 2)
                        else:
                            eid = self.quick_elem([1 + n * 10, 2 + n * 10, 3 + n * 10], eid, others, 2, True)
                        if self.layer != 1:
                            eid = self.quick_elem([1 + n * 10, 2 + (n - 1) * 10], eid, others, 2)
                            eid = self.quick_elem([1 + n * 10, 3 + (n - 1) * 10], eid, others, 2)
                else:
                    eid = self.quick_elem([1 + n * 10, 2 + n * 10, 3 + n * 10], eid, others, 2, True)
                    if n != 1:
                        eid = self.quick_elem([1 + n * 10, 2 + (n - 1) * 10], eid, others, 2)
                        eid = self.quick_elem([1 + n * 10, 3 + (n - 1) * 10], eid, others, 2)
        if add_top_brace:  # 首层加支撑
            self.add(Node(self.base_n + 51, self.pD))
            self.add(Node(self.base_n + 52, self.pE))
            self.add(Element(e=self.base_n + 1 + 50, secn=main_tube_secn, mat=1,
                             nodes=[
                                 self.node_list[self.base_n + 11],
                                 self.node_list[self.base_n + 51]]
                             ))
            self.add(Element(e=self.base_n + 1 + 51, secn=2, mat=1,
                             nodes=[
                                 self.node_list[self.base_n + 1],
                                 self.node_list[self.base_n + 52]
                             ]))

    def quick_elem(self, nlist, e0, secn, matid, closed=False):
        for i, n in enumerate(nlist):
            if n != nlist[0]:
                if type(secn) is not List:
                    s = secn
                else:
                    s = secn[i - 1]
                self.add(Element(e0, secn=s, mat=matid, nodes=[
                    self.node_list[nlist[i - 1] + self.base_n],
                    self.node_list[n + self.base_n]]
                                 ))
                e0 += 1
        if closed:
            if type(secn) is not List:
                s = secn
            else:
                s = secn[-1]
            self.add(Element(e0, secn=s, mat=matid, nodes=[
                self.node_list[nlist[- 1] + self.base_n],
                self.node_list[nlist[0] + self.base_n]]
                             ))
            e0 += 1
        return e0

    def get_e_loc(self, eid):
        n1 = self.elem_list[eid].nlist[0]
        n2 = self.elem_list[eid].nlist[1]
        return eid, 0.5 * (n1.vec + n2.vec)

    @staticmethod
    def getFg(gv, Ud, C, D, rho=Q_(1.25, ureg.kg / ureg.m ** 3)):
        """
        静风荷载
        :param gv:
        :param Ud:
        :param C:
        :param D:
        :param rho:
        :return:
        """
        Ug = Q_(gv * Ud, ureg.m / ureg.s)
        F = (0.5 * rho * Ug ** 2 * C * Q_(D, ureg.m)).to(ureg.N / ureg.m)
        return F

    @staticmethod
    def GetUd(U10, Z, kc, kf, alpha0):
        """
        基本风速换算基准风速
        :param U10: 基本风速
        :param Z: 基准高度
        :param kc: 地表类别换算系数，D=0.564
        :param kf: 抗风风险系数 R2=1.02
        :param alpha0: 地表粗糙度系数
        :return:
        """
        Us10 = kc * U10 * ureg.m / ureg.s
        Ud = kf * (Z / 10) ** alpha0 * Us10
        return Ud

    def add(self, obj):
        if isinstance(obj, Node):
            collect = self.node_list
        elif isinstance(obj, Element):
            if self.node_list.keys().__contains__(obj.nlist[0].id) and self.node_list.keys().__contains__(obj.nlist[1].id):
                collect = self.elem_list
                if obj.secn in [1, ] and int(obj.id % 1e5 // 1e4) in [2, 4, 7, 9]:
                    self.left_elem_list[obj.id] = obj
                if obj.secn in [1, ] and int(obj.id % 1e5 // 1e4) in [1, 2, 6, 7]:
                    self.front_elem_list[obj.id] = obj
            else:
                raise ValueError("节点不存在.")
        else:
            raise TypeError
        collect[obj.id] = obj
