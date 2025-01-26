import numpy as np
import pandas as pd
from ezdxf.math import Vec3

from .fem import FEM
from ..fem_base import Node, Element, Fix


class TrussUni(FEM):
    def __init__(self, slope, cell_l, cell_h_fuc, cell_w_fuc, pier_loc):
        super().__init__()
        self.slope = slope
        self.n0 = 0
        self.e2windy = []
        self.e2rq = []
        self.e2dead2 = []
        self.cell_l = cell_l
        self.cell_h = cell_h_fuc
        self.cell_w = cell_w_fuc
        self.pier_loc = pier_loc
        # self.make_sections()
        nodes, elements = self.make_fem()
        for i, row in nodes.iterrows():
            self.node_list[int(row['n'])] = Node(row['n'], row.x, row.y, row.z)
        for i, row in elements.iterrows():
            self.elem_list[int(row['e'])] = (
                Element(e=row.e, mat=row.mat, etype=188, real=188, secn=row.secn, nodes=
                [
                    self.node_list[row.ni],
                    self.node_list[row.nj]
                ]))
            if row.secn in [11]:
                self.top_elem_list[int(row['e'])] = (
                    Element(e=row.e, mat=row.mat, etype=188, real=188, secn=row.secn, nodes=
                    [
                        self.node_list[row.ni],
                        self.node_list[row.nj]
                    ]))
                if row['e'] // 1000 == 53:
                    self.left_elem_list[int(row['e'])] = (
                        Element(e=row.e, mat=row.mat, etype=188, real=188, secn=row.secn, nodes=
                        [
                            self.node_list[row.ni],
                            self.node_list[row.nj]
                        ]))
            elif row.secn in [12]:
                if row['e'] // 1000 == 54:
                    self.left_elem_list[int(row['e'])] = (
                        Element(e=row.e, mat=row.mat, etype=188, real=188, secn=row.secn, nodes=
                        [
                            self.node_list[row.ni],
                            self.node_list[row.nj]
                        ]))

        self.fix_list[2000] = Fix(2000, {'Uy': 0, 'Uz': 0})
        self.fix_list[4000] = Fix(4000, {'Uy': 0, 'Uz': 0})

    def make_fem(self):
        xlist = []
        zlist = []
        x0 = 0
        for i in range(len(self.cell_l)):
            xlist.append(x0)
            zlist.append(x0 * self.slope)
            x0 += self.cell_l[i]
        xlist.append(x0)
        zlist.append(x0 * self.slope)
        nodes = []
        elems = []
        nodes = pd.DataFrame(nodes, columns=['n', 'x', 'y', 'z'], dtype=np.float32)
        elems = pd.DataFrame(elems, columns=['e', 'ni', 'nj', 'secn', 'mat'], dtype=np.float32)
        for i, x in enumerate(xlist):
            for u in range(2):
                y = self.cell_w(x) * [-0.5, 0.5][u]
                for v, z in enumerate([zlist[i], zlist[i] - self.cell_h(x)]):
                    layer = int("%i%i" % (u, v), 2) + 1
                    node_id: int = self.n0 + i + layer * 1000
                    nodes.loc[len(nodes)] = [node_id, x, y, z]
            if self.inside(self.pier_loc, x - 1500, [-13600, 13600]):
                coord_secn = 11
                cell_secn = [12, 13, 14]
            else:
                coord_secn = 11
                cell_secn = [12, 13, 14]
            if self.inside(self.pier_loc, x, [-13600, 13600]):
                rect_secn = [12, 13, 14]
            else:
                rect_secn = [12, 13, 14]
            elems.loc[len(elems)] = [self.n0 + 10000 + i, self.n0 + 1000 + i, self.n0 + 2000 + i, 23, 2]
            elems.loc[len(elems)] = [self.n0 + 20000 + i, self.n0 + 2000 + i, self.n0 + 4000 + i, 22, 2]
            elems.loc[len(elems)] = [self.n0 + 30000 + i, self.n0 + 4000 + i, self.n0 + 3000 + i, 23, 2]
            elems.loc[len(elems)] = [self.n0 + 40000 + i, self.n0 + 3000 + i, self.n0 + 1000 + i, 21, 2]
            if i != 0:
                elems.loc[len(elems)] = [self.n0 + i + 51000, self.n0 + 1000 + i, self.n0 + 1000 + (i - 1), 11, 1]
                elems.loc[len(elems)] = [self.n0 + i + 52000, self.n0 + 2000 + i, self.n0 + 2000 + (i - 1), 12, 1]
                elems.loc[len(elems)] = [self.n0 + i + 53000, self.n0 + 3000 + i, self.n0 + 3000 + (i - 1), 11, 1]
                elems.loc[len(elems)] = [self.n0 + i + 54000, self.n0 + 4000 + i, self.n0 + 4000 + (i - 1), 12, 1]
                self.e2rq.append(self.get_e_loc(self.n0 + i + 53000, nodes, elems))
                self.e2dead2.append(self.get_e_loc(self.n0 + i + 51000, nodes, elems))
                self.e2dead2.append(self.get_e_loc(self.n0 + i + 53000, nodes, elems))
                self.e2windy.append(self.get_e_loc(self.n0 + i + 53000, nodes, elems))
                self.e2windy.append(self.get_e_loc(self.n0 + i + 54000, nodes, elems))
                if i % 2 == 0:
                    elems.loc[len(elems)] = [self.n0 + i + 55000, self.n0 + 1000 + i, self.n0 + 2000 + (i - 1), 23, 2]
                    elems.loc[len(elems)] = [self.n0 + i + 56000, self.n0 + 3000 + i, self.n0 + 4000 + (i - 1), 23, 2]
                    elems.loc[len(elems)] = [self.n0 + i + 57000, self.n0 + 3000 + i, self.n0 + 1000 + (i - 1), 21, 2]
                    elems.loc[len(elems)] = [self.n0 + i + 58000, self.n0 + 4000 + i, self.n0 + 2000 + (i - 1), 22, 2]
                else:
                    elems.loc[len(elems)] = [self.n0 + i + 55000, self.n0 + 2000 + i, self.n0 + 1000 + (i - 1), 23, 2]
                    elems.loc[len(elems)] = [self.n0 + i + 56000, self.n0 + 4000 + i, self.n0 + 3000 + (i - 1), 23, 2]
                    elems.loc[len(elems)] = [self.n0 + i + 57000, self.n0 + 2000 + i, self.n0 + 4000 + (i - 1), 21, 2]
                    elems.loc[len(elems)] = [self.n0 + i + 58000, self.n0 + 1000 + i, self.n0 + 3000 + (i - 1), 22, 2]
        return nodes, elems

    @staticmethod
    def inside(locs, x0, ranges):
        for lc in locs:
            if (x0 - lc >= ranges[0]) and (x0 - lc <= ranges[1]):
                return True
        return False

    @staticmethod
    def get_e_loc(eid, nodes, elems):
        n1 = elems[elems['e'] == eid]['ni'].values[0]
        n2 = elems[elems['e'] == eid]['nj'].values[0]
        n1 = nodes[nodes['n'] == n1]
        n2 = nodes[nodes['n'] == n2]
        p1 = Vec3(float(n1.x.values[0]), float(n1.y.values[0]), float(n1.z.values[0]))
        p2 = Vec3(float(n2.x.values[0]), float(n2.y.values[0]), float(n2.z.values[0]))
        return eid, 0.5 * (p1 + p2)

#     def make_sections(self):
#         self.sect_list = {
#             11: BoxSection(Id=11, Name="上弦杆", offset=(0, 0), w1=400, w2=250, t1=12, t2=12, t3=12, t4=12),
#             12: BoxSection(Id=12, Name="下弦杆", offset=(0, 0), w1=400, w2=250, t1=12, t2=12, t3=12, t4=12),
#             21: ISection(Id=21, Name="上平联", offset=(0, 200), w1=194, w2=150, w3=150, t1=9, t2=9, t3=6),
#             22: ISection(Id=22, Name="下平联", offset=(0, 200), w1=194, w2=150, w3=150, t1=9, t2=9, t3=6),
#             23: ISection(Id=23, Name="腹杆", offset=(0, 0), w1=194, w2=150, w3=150, t1=9, t2=9, t3=6),
#             31: BoxSection(Id=31, Name="墩顶弦杆", offset=(0, 0), w1=400, w2=400, t1=20, t2=20, t3=20, t4=20),
#             32: BoxSection(Id=32, Name="墩顶上平联", offset=(0, 200), w1=350, w2=250, t1=10, t2=10, t3=10, t4=10),
#             33: BoxSection(Id=33, Name="墩顶下平联", offset=(0, 200), w1=350, w2=250, t1=10, t2=10, t3=10, t4=10),
#             34: BoxSection(Id=34, Name="墩顶腹杆", offset=(0, 0), w1=350, w2=250, t1=10, t2=10, t3=10, t4=10)
#         }
#