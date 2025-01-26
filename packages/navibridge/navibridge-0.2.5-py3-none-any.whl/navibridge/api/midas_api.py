import os
import shutil

import numpy as np

from .base_api import BaseAPI
from ..zoo import FEM


class MidasDRS:
    def __init__(self, bridge_type, site_type, intensity, Tg, kesi, seismic_type, is_vertical, Tmax, delt_t):
        """

        :param bridge_type: 桥梁类别
        :param site_type: 场地类别（"I0", "I1", "II", "III", "IV"）
        :param intensity:  设防烈度（"VI", "VII", "VII+", "VIII", "VIII+", "IX", ）
        :param Tg:  分区特征周期 （0.35, 0.4, 0.45）
        :param kesi: 阻尼比
        :param seismic_type: 反应谱类别（"E1","E2"）
        :param is_vertical: 是否为竖向地震
        :param Tmax: 生成长度
        """
        self.specification = "JTG/T 2231-01-2020"

        assert Tg in [0.35, 0.4, 0.45]
        assert site_type in ["I0", "I1", "II", "III", "IV"]
        assert intensity in ["VI", "VII", "VII+", "VIII", "VIII+", "IX", ]
        self.Tg = Tg
        self.bridge_type = bridge_type
        self.seismic_type = seismic_type
        self.intensity = intensity
        self.damper_ratio = kesi
        self.site_type = site_type
        self.isVertical = is_vertical
        self.A = self.get_A(intensity)
        self.Ci = self.get_Ci(seismic_type, bridge_type)
        self.Cd = self.get_Cd(kesi)
        self.Cs = self.get_Cs(site_type, intensity, is_vertical)
        self.Tg_real = self.get_Tgft(site_type, Tg, is_vertical)
        self.Smax = self.get_Smax(self.Ci, self.Cs, self.Cd, self.A)
        self.Tmax = Tmax
        self.ts, self.ss = self.get_DES(delt_t)
        self.parameters = self.get_para_mct()

    def get_para_mct(self):

        if self.site_type == "I0":
            st = 1
        elif self.site_type == "I1":
            st = 2
        elif self.site_type == "II":
            st = 3
        elif self.site_type == "III":
            st = 4
        elif self.site_type == "IV":
            st = 5
        else:
            raise KeyError

        if self.intensity == "VI":
            it = "6(0.05g)"
        elif self.intensity == "VII":
            it = "7(0.1g)"
        elif self.intensity == "VII+":
            it = "7(0.15g)"
        elif self.intensity == "VIII":
            it = "8(0.2g)"
        elif self.intensity == "VIII+":
            it = "8(0.3g)"
        elif self.intensity == "IX":
            it = "9(0.4g)"
        else:
            raise KeyError
        isv = 1 if self.isVertical else 0
        return ("   %s, %s, %.2f, %i, %s, %s,%.2f, %.2f, %.2f, %.2f, %.2f, %.8f, %.2f,%.2f, 0, %i\n"
                % (
                    self.specification,
                    self.bridge_type,
                    self.Tg,
                    st, it, self.seismic_type, self.Tg_real, self.Ci, self.Cs, self.Cd, self.A, self.Smax,
                    self.Tmax, self.damper_ratio, isv
                )
                )

    def get_DES(self, step):
        Tlist = np.linspace(0, self.Tmax, int(np.round((self.Tmax - 0) / step + 1))).tolist()
        Tlist.append(0.1)
        Tlist.append(self.Tg_real)
        Tlist = list(set(Tlist))
        Tlist.sort()
        Slist = [self.get_S(self.Smax, self.Tg_real, ti) for ti in Tlist]
        return Tlist, Slist

    @staticmethod
    def get_S(Smax, Tg, T):
        T0 = 0.1
        if T < T0:
            return Smax * (0.6 * T / T0 + 0.4)
        elif T < Tg:
            return Smax
        else:
            return Smax * (Tg / T)

    @staticmethod
    def get_Smax(Ci, Cs, Cd, A):
        return 2.5 * Ci * Cs * Cd * A

    @staticmethod
    def get_Cs(site_type, intensity, isV):
        res = [
            [0.72, 0.74, 0.75, 0.76, 0.85, 0.9],
            [0.80, 0.82, 0.83, 0.85, 0.95, 1.0],
            [1.00, 1.00, 1.00, 1.00, 1.00, 1.0],
            [1.30, 1.25, 1.15, 1.00, 1.00, 1.0],
            [1.25, 1.20, 1.10, 1.00, 0.95, 0.9],
        ]
        resV = [
            [0.6, 0.6, 0.6, 0.6, 0.6, 0.6],
            [0.6, 0.6, 0.6, 0.6, 0.7, 0.7],
            [0.6, 0.6, 0.6, 0.6, 0.7, 0.8],
            [0.7, 0.7, 0.7, 0.8, 0.8, 0.8],
            [0.8, 0.8, 0.8, 0.9, 0.9, 0.8],
        ]
        ridx = ["I0", "I1", "II", "III", "IV"].index(site_type)
        cidx = ["VI", "VII", "VII+", "VIII", "VIII+", "IX", ].index(intensity)
        if isV:
            return resV[ridx][cidx]
        else:
            return res[ridx][cidx]

    @staticmethod
    def get_Tgft(site_type, Tg, isV):
        if not isV:
            if Tg == 0.35:
                if site_type == "I0":
                    return 0.20
                elif site_type == "I1":
                    return 0.25
                elif site_type == "II":
                    return 0.35
                elif site_type == "III":
                    return 0.45
                elif site_type == "IV":
                    return 0.65
                else:
                    raise KeyError
            elif Tg == 0.40:
                if site_type == "I0":
                    return 0.25
                elif site_type == "I1":
                    return 0.30
                elif site_type == "II":
                    return 0.40
                elif site_type == "III":
                    return 0.55
                elif site_type == "IV":
                    return 0.75
                else:
                    raise KeyError
            elif Tg == 0.45:
                if site_type == "I0":
                    return 0.30
                elif site_type == "I1":
                    return 0.35
                elif site_type == "II":
                    return 0.45
                elif site_type == "III":
                    return 0.65
                elif site_type == "IV":
                    return 0.90
                else:
                    raise KeyError(site_type)
        else:
            if Tg == 0.35:
                if site_type == "I0":
                    return 0.15
                elif site_type == "I1":
                    return 0.20
                elif site_type == "II":
                    return 0.25
                elif site_type == "III":
                    return 0.30
                elif site_type == "IV":
                    return 0.55
                else:
                    raise KeyError
            elif Tg == 0.40:
                if site_type == "I0":
                    return 0.20
                elif site_type == "I1":
                    return 0.25
                elif site_type == "II":
                    return 0.30
                elif site_type == "III":
                    return 0.35
                elif site_type == "IV":
                    return 0.60
                else:
                    raise KeyError
            elif Tg == 0.45:
                if site_type == "I0":
                    return 0.25
                elif site_type == "I1":
                    return 0.30
                elif site_type == "II":
                    return 0.40
                elif site_type == "III":
                    return 0.50
                elif site_type == "IV":
                    return 0.75
                else:
                    raise KeyError

    @staticmethod
    def get_Cd(xi):
        return max(1 + (0.05 - xi) / (0.08 + 1.6 * xi), 0.55)

    @staticmethod
    def get_Ci(seismic_type, bridge_type):
        if seismic_type == "E1":
            if bridge_type == "A":
                return 1.0
            elif bridge_type == "B":
                return 0.43
            elif bridge_type == "C":
                return 0.34
            elif bridge_type == "D":
                return 0.23
            else:
                raise KeyError
        elif seismic_type == "E2":
            if bridge_type == "A":
                return 1.7
            elif bridge_type == "B":
                return 1.3
            elif bridge_type == "C":
                return 1.0
            elif bridge_type == "D":
                raise KeyError
            else:
                raise KeyError
        else:
            raise KeyError
        pass

    @staticmethod
    def get_A(intensity):
        if intensity == "VI":
            return 0.05
        elif intensity == "VII":
            return 0.10
        elif intensity == "VII+":
            return 0.15
        elif intensity == "VIII":
            return 0.20
        elif intensity == "VIII+":
            return 0.30
        elif intensity == "IX":
            return 0.40
        else:
            raise KeyError


class MidasAPI(BaseAPI):

    def __init__(self, project, root_path, init=True):
        super().__init__(project, root_path, init)
        self.options = {}
        self.fem: 'FEM' = None
        self.project_name = project
        wdr = os.path.join(root_path, self.project_name)
        self.cwd = os.path.abspath(wdr)
        self.res_dir = os.path.join(os.path.abspath(root_path), f'{project}_result.txt')
        self.init = init
        if init:
            if not os.path.exists(wdr):
                os.mkdir(wdr)
            else:
                shutil.rmtree(wdr)
                os.mkdir(wdr)

    def run_fem(self, fem_model: FEM):
        self.fem = fem_model
        file_out = open(os.path.join(self.cwd, self.project_name + '.mct'), 'w+', encoding='GBK')
        self._begin(file_out)
        self._temp(file_out)
        self._sections(file_out)
        self._nodes(file_out)
        self._elems(file_out)
        self._constraint(file_out)
        self.to_mct_rq(file_out, self.loads['rq'])
        self.to_mct_dead2(file_out, self.loads['dw'], self.loads['snow'])
        self.to_mct_wind(file_out, 20, 40, 0.785, 0.22, 1.26, 0.87, 40, truss_height_m=3.0)
        if self.loads.keys().__contains__("e1"):
            self.to_mct_seismic(file_out, self.loads['e1'], self.loads['e2'])
        file_out.close()

    def _begin(self, fid):
        fid.write("*UNIT\n")
        fid.write("N, mm, KJ, C\n")
        fid.write("*STRUCTYPE\n")
        fid.write("0,1,1,NO,YES,9806,0,NO,NO,NO\n")
        if len(self.fem.mat_list) != 0:
            fid.write("*MATERIAL \n")
            for ky in self.fem.mat_list.keys():
                m = self.fem.mat_list[ky]
                fid.write(m.mct_str)
                fid.write('\n')
        fid.write("*STLDCASE\n")
        fid.write("; LCNAME, LCTYPE, DESC\n")
        fid.write("   自重 , USER, \n")
        fid.write("   二期 , USER, \n")
        fid.write("   W1主梁横风, USER, \n")
        fid.write("   W1立柱横风, USER, \n")
        fid.write("   W1立柱纵风, USER, \n")
        fid.write("   W2主梁横风, USER, \n")
        fid.write("   W2立柱横风, USER, \n")
        fid.write("   W2立柱纵风, USER, \n")
        fid.write("   整体升温, USER, \n")
        fid.write("   整体降温, USER, \n")
        fid.write("   雪荷载, USER, \n")
        fid.write("*USE-STLD, 自重\n")
        fid.write("*SELFWEIGHT\n")
        fid.write("0, 0, -1,\n")

    def _temp(self, fid):
        fid.write("*USE-STLD, 整体升温\n")
        fid.write("*SYSTEMPER\n")
        fid.write(f"{self.loads['temp_up']}, \n")
        fid.write("*USE-STLD, 整体降温\n")
        fid.write("*SYSTEMPER\n")
        fid.write(f"{self.loads['temp_down']}, \n")

    def _sections(self, fid):
        fid.write("*SECTION\n")
        for ky in self.fem.sect_list.keys():
            s = self.fem.sect_list[ky]
            if hasattr(s, 'mct_str'):
                fid.write(s.mct_str)

    def _nodes(self, fid):
        fid.write("*NODE\n")
        for n in self.fem.node_list.keys():
            nd = self.fem.node_list[n]
            fid.write("%i,%.6f,%.6f,%.6f\n" % (nd.id, nd.x, nd.y, nd.z))

    def _elems(self, fid):
        fid.write("*ELEMENT\n")
        for ky in self.fem.elem_list.keys():
            e = self.fem.elem_list[ky]
            if len(e.nlist) == 4:
                #   5060, PLATE ,    1,     1,  7001,  7002,  2002,  2001,     1,     0
                n1 = e.nlist[0].id
                n2 = e.nlist[1].id
                n3 = e.nlist[2].id
                n4 = e.nlist[3].id
                iMat = e.mat
                iSecn = e.secn
                fid.write(" %i,PLATE,%i,%i,%i,%i,%i,%i,1,0\n" % (e.id, iMat, iSecn, n1, n2, n3, n4))
            else:
                n1 = e.nlist[0].id
                n2 = e.nlist[1].id
                iMat = e.mat
                iSecn = e.secn
                beta = 90 if (iSecn == 15 or iSecn == 17) else 0
                fid.write(" %i,BEAM,%i,%i,%i,%i,%i,0\n" % (e.id, iMat, iSecn, n1, n2, beta))

    def _constraint(self, fid):
        fid.write("*CONSTRAINT    ; Supports\n")
        for ky in self.fem.fix_list.keys():
            f = self.fem.fix_list[ky]
            if hasattr(f, 'mct_str'):
                fid.write(f.mct_str)

    def to_mct_dead2(self, fid, dw2, snow):
        e2dead2 = [e for e in self.fem.top_elem_list.keys() if e // 1000 == 51 or e // 1000 == 53]
        e2dead2.sort()
        if len(e2dead2) != 0:
            fid.write("*USE-STLD,二期\n")
            fid.write("*BEAMLOAD \n")
        for ee in e2dead2:
            fid.write(
                " %i, BEAM   , UNILOAD, GZ, NO , NO, aDir[1], , , , 0, %.3f, 1, %.3f, 0, 0, 0, 0, , NO, 0, 0, NO, \n" % (
                    ee, -dw2 * 0.5, -dw2 * 0.5))
        fid.write("*USE-STLD,雪荷载\n")
        fid.write("*BEAMLOAD \n")
        for ee in e2dead2:
            fid.write(
                " %i, BEAM   , UNILOAD, GZ, NO , NO, aDir[1], , , , 0, %.3f, 1, %.3f, 0, 0, 0, 0, , NO, 0, 0, NO, \n" % (
                    ee, -snow * 0.5, -snow * 0.5))

    def to_mct_rq(self, fid, rq):
        fid.write("*MVLDCODE\n")
        fid.write("   CODE=CHINA\n")
        fid.write("*LINELANE(CH) \n")
        fid.write("   NAME=L, LANE, , 0, 0, BOTH, 500, 3000, NO, 3000\n")
        e2rq = [e for e in self.fem.top_elem_list.keys() if e // 1000 == 53]
        e2rq.sort()
        for ii, e in enumerate(e2rq):
            if ii == 0:
                st = "YES"
                ed = ", "
            elif ii != len(e2rq) - 1:
                st = "NO"
                if ii % 2 != 0:
                    ed = '\n'
                else:
                    ed = ", "
            else:
                st = "NO"
                ed = '\n'
            fid.write("     %i, %f, 120000, %s ,1 %s" % (e, 2250, st, ed))
        fid.write("*VEHICLE\n")
        fid.write(f"   NAME=专用人行荷载, 2, CROWD, 1, {rq}\n")
        fid.write("*MVLDCASE(CH)   \n")
        fid.write("   NAME=RQ, , NO, 2, 1, 0\n")
        fid.write("        1, 1, 0.8, 0.67, 0.6, 0.55, 0.55, 0.55\n")
        fid.write("        1, 1, 0.78, 0.67, 0.6, 0.55, 0.52, 0.5\n")
        fid.write("        1.2, 1, 0.78, 0.67, 0.6, 0.55, 0.52, 0.5\n")
        fid.write("        VL, 专用人行荷载, 1, 0, 1, L\n")
        fid.write("*MOVE-CTRL(CH) \n")
        fid.write("   INF, 0, 3, NODAL, NO, AXIAL, YES,   YES, NO, ,   YES, NO, ,   YES, NO, ,   YES, NO,   , NO, 0, 0, YES, 0\n")
        fid.write("   0\n")

    # def to_mct_wind(self, fid, U10W1, U10W2, kc, alpha0, gv, CY, func_D):
    def to_mct_wind(self, fid, U10W1, U10W2, kc, alpha0, gv, CY, truss_z0_m, truss_height_m):
        zz0 = truss_z0_m
        UdW1 = self.GetUd(U10W1, zz0, kc, 1, alpha0).m
        FgW1 = self.getFg(gv, UdW1, CY, truss_height_m).m * 1e-3  # N/mm
        UdW2 = self.GetUd(U10W2, zz0, kc, 1, alpha0).m
        FgW2 = self.getFg(gv, UdW2, CY, truss_height_m).m * 1e-3  # N/mm

        e2windy_beam = [e for e in self.fem.left_elem_list.keys() if e < 1e5]  # or e // 1000 == 54]
        fid.write("*USE-STLD,W1主梁横风\n")
        fid.write("*BEAMLOAD \n")
        for ee in e2windy_beam:
            fid.write(
                " %i, BEAM , UNILOAD, GY, NO , NO, aDir[1], , , , 0, %.3f, 1, %.3f, 0, 0, 0, 0, , NO, 0, 0, NO, \n" % (
                    ee, -FgW1 * 0.5, -FgW1 * 0.5))
        fid.write("*USE-STLD,W2主梁横风\n")
        fid.write("*BEAMLOAD \n")
        for ee in e2windy_beam:
            fid.write(
                " %i, BEAM , UNILOAD, GY, NO , NO, aDir[1], , , , 0, %.3f, 1, %.3f, 0, 0, 0, 0, , NO, 0, 0, NO, \n" % (
                    ee, -FgW2 * 0.5, -FgW2 * 0.5))
        e2windx_tower = [e for e in self.fem.left_elem_list.keys() if e > 1e5]
        fid.write("*USE-STLD,W1立柱横风\n")
        fid.write("*BEAMLOAD \n")
        for ee in e2windx_tower:
            ele = self.fem.elem_list[ee]
            z0 = ele.location[0] * 1e-3 * self.options['slope'] - self.options['truss_h'] * 1e-3
            dist = z0 - ele.location[2] * 1e-3
            zi = zz0 - dist
            dx = self.options['k_l'] * dist
            D = self.options['truss_l'] * 1e-3 + 2 * dx
            zi = max(zi, 0.1)
            UdW1 = self.GetUd(U10W1, zi, kc, 1, alpha0).m
            FgW1 = self.getFg(gv, UdW1, CY, D).m * 1e-3  # N/mm
            fid.write(
                " %i, BEAM , UNILOAD, GY, NO , NO, aDir[1], , , , 0, %.3f, 1, %.3f, 0, 0, 0, 0, , NO, 0, 0, NO, \n" % (
                    ee, -FgW1 * 0.5, -FgW1 * 0.5))
        fid.write("*USE-STLD,W2立柱横风\n")
        fid.write("*BEAMLOAD \n")
        for ee in e2windx_tower:
            ele = self.fem.elem_list[ee]
            z0 = ele.location[0] * 1e-3 * self.options['slope'] - self.options['truss_h'] * 1e-3
            dist = z0 - ele.location[2] * 1e-3
            zi = zz0 - dist
            dx = self.options['k_l'] * dist
            D = self.options['truss_l'] * 1e-3 + 2 * dx
            zi = max(zi, 0.1)
            UdW2 = self.GetUd(U10W2, zi, kc, 1, alpha0).m
            FgW2 = self.getFg(gv, UdW2, CY, D).m * 1e-3  # N/mm
            fid.write(
                " %i, BEAM , UNILOAD, GY, NO , NO, aDir[1], , , , 0, %.3f, 1, %.3f, 0, 0, 0, 0, , NO, 0, 0, NO, \n" % (
                    ee, -FgW2 * 0.5, -FgW2 * 0.5))
        return

    def to_mct_seismic(self, fid, spa_e1: MidasDRS, spa_e2: MidasDRS):
        fid.write("*UNIT\n")
        fid.write("N, mm, KJ, C\n")
        fid.write("*SFUNCTION    ; Spectrum Function\n")
        fid.write("   FUNC=E1DRS, 1, 0, 1, 9806, %.2f, , 1.000000\n" % spa_e1.damper_ratio)
        fid.write(spa_e1.parameters)
        i = 1
        for t, s in zip(spa_e1.ts, spa_e1.ss):
            fid.write("    %8.5f, %12.9f" % (t, s))
            if i % 2 == 0:
                fid.write("\n")
            else:
                fid.write(",    ")
            i += 1
        fid.write("   FUNC=E2DRS, 1, 0, 1, 9806, %.2f, , 1.000000\n" % spa_e2.damper_ratio)
        fid.write(spa_e2.parameters)
        i = 1
        for t, s in zip(spa_e2.ts, spa_e2.ss):
            fid.write("    %8.5f, %12.9f" % (t, s))
            if i % 2 == 0:
                fid.write("\n")
            else:
                fid.write(",    ")
            i += 1

        fid.write("*SPLDCASE \n")
        for E in ['E1', 'E2']:
            for direction in ['X', "Y"]:
                fid.write("   NAME=%s%s, XY, 0, 1, 1, NO, NO, LOG,\n" % (E, direction))
                fid.write("        CQC, NO, 0, YES\n")
                fid.write("        %sDRS\n        " % E)
                for j in range(240):
                    fid.write("YES, 1")
                    if j != 239:
                        fid.write(",")
                    else:
                        fid.write("\n")
        fid.write("*EIGEN-CTRL    ; Eigenvalue Analysis Control\n")
        fid.write("   RITZ, NO, 0\n")
        fid.write("   GROUND, ACCX, 80, GROUND, ACCY, 80, GROUND, ACCZ, 80\n")

    def clear(self):
        if self.init:
            shutil.rmtree(self.cwd)
        pass
