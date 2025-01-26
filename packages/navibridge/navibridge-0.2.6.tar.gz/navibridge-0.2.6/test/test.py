from ezdxf.math import Vec3
from scipy.interpolate import interp1d

from navibridge.api import MidasAPI
from navibridge.api.midas_api import MidasDRS
from navibridge.fem_base import Material
from navibridge.fem_base.section import TubeSection, BoxSection, ISection
from navibridge.zoo import TrussUni, SectionGroup
from navibridge.zoo.tower import easy_tower


def h_func_uni(x):
    return 2500


def w_func_uni4(x):
    return 2500


def main(
        wk_name,
        sp_n,
        tower_h,
        k_l,
        k_w,
        truss_l,
        truss_h,
        truss_w,
        slope,
        deltH,
        targetA,
):
    truss_n = int(sum(sp_n))
    func_w_1 = interp1d([0, -1000000], [truss_w, truss_w + 2 * 1000000 * k_w], kind='linear')
    func_l_1 = interp1d([0, -1000000], [truss_l, truss_l + 2 * 1000000 * k_l], kind='linear')
    sps = [n * truss_l * 1e-3 for n in sp_n]
    pi_xx = [0]
    for s in sps[0:-1]:
        pi_xx.append(pi_xx[-1] + s * 1000)
    pi_xx.remove(0)
    pi_zz = [slope * x - (truss_h + deltH) for x in pi_xx]
    tower_n = 1
    m1 = Material(1, 2.06e5, 7.85e-9, 1.2e-5, 0.3, 'Q420')
    m2 = Material(2, 2.06e5, 7.85e-9, 1.2e-5, 0.3, 'Q355')

    md = TrussUni(slope=slope, cell_l=[truss_l, ] * truss_n, cell_h_fuc=h_func_uni, cell_w_fuc=w_func_uni4, pier_loc=pi_xx)
    md.mat_list[1] = m1
    md.mat_list[2] = m2
    for i in range(len(tower_h)):
        x, y = list(zip(pi_xx, pi_zz))[i]
        md += easy_tower(tower_n, Vec3(x, 0, y), tower_h[tower_n - 1], -max(tower_h), func_l_1, func_w_1,
                         delta_l=truss_l, delta_h=deltH, s=slope, targe_ang=targetA)
        tower_n += 1
    ss = SectionGroup()
    ss.add(TubeSection(Id=1, Name="D1", offset=(0, 0), d=400, t=8))
    ss.add(TubeSection(Id=2, Name="D2", offset=(0, 0), d=300, t=6))
    ss.add(TubeSection(Id=3, Name="D2", offset=(0, 0), d=300, t=6))
    ss.add(TubeSection(Id=4, Name="D2", offset=(0, 0), d=200, t=4))
    ss.add(TubeSection(Id=9, Name="D9", offset=(0, 0), d=200, t=4))

    ss.add(ISection(Id=11, Name="上弦杆", offset=(0, 0), w1=200, w2=200, w3=400, t1=13, t2=13, t3=8))
    ss.add(ISection(Id=12, Name="下弦杆", offset=(0, 0), w1=200, w2=200, w3=400, t1=13, t2=13, t3=8))
    ss.add(ISection(Id=21, Name="上平联", offset=(0, 0), w1=150, w2=150, w3=200, t1=9, t2=9, t3=6))
    ss.add(ISection(Id=22, Name="下平联", offset=(0, 0), w1=150, w2=150, w3=200, t1=9, t2=9, t3=6))
    ss.add(ISection(Id=23, Name="腹杆", offset=(0, 0), w1=150, w2=150, w3=200, t1=9, t2=9, t3=6))

    api = MidasAPI(project=wk_name, root_path=".", init=True)
    api.load_config(
        rq=5.25,
        dw=1.6,
        snow=0.3,
        w1=20,
        w2=30,
        temp_up=15,
        temp_down=-10,
        e1=MidasDRS("A", "I0", "VI", 0.45, 0.03, "E1", False, 6, 0.06),
        e2=MidasDRS("A", "I0", "VI", 0.45, 0.03, "E2", False, 6, 0.06),
    )
    api.config(
        truss_h=truss_h,
        truss_l=truss_l,
        slope=slope,
        k_l=k_l,
        k_w=k_w,
    )
    api.run_fem(ss + md)
    api.write_dxf('test.dxf')


if __name__ == '__main__':
    sps = [51.25, ] + [60, ] * 3 + [57.5, ] * 2 + [60, ] * 3 + [57.5] + [1.25]
    spn = [n / 2.5 for n in sps]
    th = [13.5, 25.75, 37.5, 46.5, 42, 37.5, 29.5, 42.0, 42, 33.5]
    main(wk_name="FG2",
         sp_n=spn,
         tower_h=th,
         k_l=4 / 100,
         k_w=5 / 100,
         truss_l=2500,
         truss_h=2500,
         truss_w=2500,
         slope=-0.025,
         deltH=800,
         targetA=30,
         )
