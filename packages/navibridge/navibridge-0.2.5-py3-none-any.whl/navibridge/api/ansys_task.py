from typing import List
from ezdxf.math import Vec3
from scipy.interpolate import interp1d
from .ansys_api import AnsysAPI
from ..fem_base import Material
from ..zoo import SectionGroup, TrussUni
from ..fem_base.section import TubeSection, BoxSection, ISection
from ..zoo.tower import easy_tower


class AnsysTask:
    def __init__(self, root_path, wk_name, sp_n: List[float], tower_h: List[float], k_l, k_w,
                 truss_l, truss_h, truss_w, slope, tower_sec_category, truss_sec_category, deltH=800):
        super().__init__()
        self.config = {}
        self.loads_config = {}
        self.dimension_config = {}
        self.root_path = root_path
        self.wk_name = wk_name
        self.sp_n = sp_n
        self.tower_h = tower_h
        self.k_l = k_l
        self.k_w = k_w
        self.truss_l = truss_l
        self.truss_h = truss_h
        self.truss_w = truss_w
        self.slope = slope
        self.deltH = deltH
        self.dimension_config['length'] = sum(sp_n) * truss_l * 1e-3
        self.dimension_config['truss'] = (truss_h, truss_w, truss_l)
        self.dimension_config['slope'] = slope
        self.dimension_config['kl_kw'] = (k_l, k_w)
        self.tower_sect_category = tower_sec_category
        self.truss_sec_category = truss_sec_category

    def h_func_uni(self, x):
        return self.truss_h

    def w_func_uni4(self, x):
        return self.truss_w

    def perform_task(self):
        sp_n = self.sp_n
        tower_h: List[float] = self.tower_h
        k_l, k_w = self.k_l, self.k_w
        truss_l, truss_h, truss_w = self.truss_l, self.truss_h, self.truss_w
        slope = self.slope
        deltH = self.deltH
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
        md = TrussUni(slope=slope, cell_l=[truss_l, ] * truss_n,
                      cell_h_fuc=self.h_func_uni,
                      cell_w_fuc=self.w_func_uni4,
                      pier_loc=pi_xx
                      )
        for i in range(len(tower_h)):
            x, y = list(zip(pi_xx, pi_zz))[i]
            md += easy_tower(tower_n, Vec3(x, 0, y), tower_h[tower_n - 1], -max(tower_h), func_l_1, func_w_1,
                             delta_l=truss_l, delta_h=deltH, s=slope)
            tower_n += 1
        ss = SectionGroup()
        if self.tower_sect_category == 'ClassA':
            ss.add(TubeSection(Id=1, Name="D1", offset=(0, 0), d=400, t=10))
            ss.add(TubeSection(Id=2, Name="D2", offset=(0, 0), d=300, t=6))
            ss.add(TubeSection(Id=3, Name="D3", offset=(0, 0), d=300, t=6))
            ss.add(TubeSection(Id=4, Name="D4", offset=(0, 0), d=200, t=4))
            ss.add(TubeSection(Id=9, Name="D9", offset=(0, 0), d=200, t=4))
        elif self.tower_sect_category == 'ClassB':
            ss.add(TubeSection(Id=1, Name="D1", offset=(0, 0), d=600, t=12))
            ss.add(TubeSection(Id=2, Name="D2", offset=(0, 0), d=400, t=10))
            ss.add(TubeSection(Id=3, Name="D3", offset=(0, 0), d=400, t=10))
            ss.add(TubeSection(Id=4, Name="D4", offset=(0, 0), d=300, t=6))
            ss.add(TubeSection(Id=9, Name="D9", offset=(0, 0), d=200, t=4))
        elif self.tower_sect_category == 'ClassC':
            ss.add(TubeSection(Id=1, Name="D1", offset=(0, 0), d=800, t=16))
            ss.add(TubeSection(Id=2, Name="D2", offset=(0, 0), d=600, t=12))
            ss.add(TubeSection(Id=3, Name="D3", offset=(0, 0), d=600, t=12))
            ss.add(TubeSection(Id=4, Name="D4", offset=(0, 0), d=300, t=6))
            ss.add(TubeSection(Id=9, Name="D9", offset=(0, 0), d=200, t=4))
        else:
            raise NotImplementedError

        if self.truss_sec_category == 'ClassA':
            ss.add(ISection(Id=11, Name="上弦杆", offset=(0, 0), w1=200, w2=200, w3=400, t1=13, t2=13, t3=8))
            ss.add(ISection(Id=12, Name="下弦杆", offset=(0, 0), w1=200, w2=200, w3=400, t1=13, t2=13, t3=8))
            ss.add(ISection(Id=21, Name="上平联", offset=(0, 0), w1=150, w2=150, w3=200, t1=9, t2=9, t3=6))
            ss.add(ISection(Id=22, Name="下平联", offset=(0, 0), w1=150, w2=150, w3=200, t1=9, t2=9, t3=6))
            ss.add(ISection(Id=23, Name="腹杆", offset=(0, 0), w1=150, w2=150, w3=200, t1=9, t2=9, t3=6))
        elif self.truss_sec_category == 'ClassB':
            ss.add(BoxSection(Id=11, Name="上弦杆", offset=(0, 0), w1=400, w2=250, t1=12, t2=12, t3=12, t4=12))
            ss.add(BoxSection(Id=12, Name="下弦杆", offset=(0, 0), w1=400, w2=250, t1=12, t2=12, t3=12, t4=12))
            ss.add(ISection(Id=21, Name="上平联", offset=(0, 0), w1=150, w2=150, w3=200, t1=9, t2=9, t3=6))
            ss.add(ISection(Id=22, Name="下平联", offset=(0, 0), w1=150, w2=150, w3=200, t1=9, t2=9, t3=6))
            ss.add(ISection(Id=23, Name="腹杆", offset=(0, 0), w1=175, w2=175, w3=250, t1=11, t2=11, t3=7))
        elif self.truss_sec_category == 'ClassC':
            ss.add(BoxSection(Id=11, Name="上弦杆", offset=(0, 0), w1=400, w2=300, t1=18, t2=18, t3=18, t4=18))
            ss.add(BoxSection(Id=12, Name="下弦杆", offset=(0, 0), w1=400, w2=300, t1=18, t2=18, t3=18, t4=18))
            ss.add(ISection(Id=21, Name="上平联", offset=(0, 0), w1=150, w2=150, w3=200, t1=9, t2=9, t3=6))
            ss.add(ISection(Id=22, Name="下平联", offset=(0, 0), w1=150, w2=150, w3=200, t1=9, t2=9, t3=6))
            ss.add(ISection(Id=23, Name="腹杆", offset=(0, 0), w1=200, w2=200, w3=300, t1=14, t2=14, t3=9))
        else:
            raise NotImplementedError
        ss.add(Material(1, 2.06e5, 7.85e-9 * self.loads_config['dc_factor'], 1.2e-5, 0.3, 'Q420'))
        ss.add(Material(2, 2.06e5, 7.85e-9 * self.loads_config['dc_factor'], 1.2e-5, 0.3, 'Q355'))

        api = AnsysAPI(project=self.wk_name, root_path=self.root_path, init=self.config['init'])
        api.config(
            image=self.config['image'],
            only_cmd=self.config['only_cmd'],
            ANSYS_PATH=self.config['ANSYS_PATH'],
        )
        api.run_fem(ss + md)
        api.run_deadload(lcn=1)
        api.run_dw(lcn=2)
        api.run_rq(self.loads_config['RQ'], lcn=6)
        api.run_wind('W1', self.loads_config['W1'], pi_xx, [2. / 3. * h for h in tower_h], max(tower_h), truss_h * 1e-3, lcn=31)
        api.run_wind('W2', self.loads_config['W2'], pi_xx, [2. / 3. * h for h in tower_h], max(tower_h), truss_h * 1e-3, lcn=32)
        api.run_wind('W3', self.loads_config['W3'], pi_xx, [2. / 3. * h for h in tower_h], max(tower_h), truss_h * 1e-3, lcn=33)
        api.run_wind('W4', self.loads_config['W4'], pi_xx, [2. / 3. * h for h in tower_h], max(tower_h), truss_h * 1e-3, lcn=34)
        api.run_wind('W5', self.loads_config['W5'], pi_xx, [2. / 3. * h for h in tower_h], max(tower_h), truss_h * 1e-3, lcn=35)
        api.run_wind('W6', self.loads_config['W6'], pi_xx, [2. / 3. * h for h in tower_h], max(tower_h), truss_h * 1e-3, lcn=36)
        api.run_tu("TU",
                   temp_up=self.loads_config['TempUp'],
                   temp_down=self.loads_config['TempDown'], lcn=40)
        api.run_se('SE', val=self.loads_config['SE'], num_tower=len(tower_h), lcn=5)
        api.run_lcomb("ULS", conf={
            81: [(1, 1.2), (2, 1.2), (5, 1.0), (31, 1.4), (41, 1.05), ],
            82: [(1, 1.2), (2, 1.2), (5, 1.0), (32, 1.4), (41, 1.05), ],
            83: [(1, 1.2), (2, 1.2), (5, 1.0), (33, 1.4), (41, 1.05), ],
            84: [(1, 1.2), (2, 1.2), (5, 1.0), (34, 1.4), (41, 1.05), ],
            85: [(1, 1.2), (2, 1.2), (5, 1.0), (35, 1.4), (41, 1.05), ],
            86: [(1, 1.2), (2, 1.2), (5, 1.0), (36, 1.4), (41, 1.05), ],
        })
        api.init_records(self.dimension_config, self.loads_config)
        api.run_mode(self.loads_config['MODEL'])
        api.run_rs("e1dx", lcn=51, direction="X", Ci=1.3, Cs=1.0, A=self.loads_config['E1'], Tg=0.35)  # 0.05g
        api.run_rs("e1dy", lcn=52, direction="Y", Ci=1.3, Cs=0.6, A=self.loads_config['E1'], Tg=0.25)  # 0.05g
        api.run_rs("e1dz", lcn=53, direction="Z", Ci=1.3, Cs=1.0, A=self.loads_config['E1'], Tg=0.35)  # 0.05g
        api.run_rs("e2dx", lcn=54, direction="X", Ci=1.3, Cs=1.0, A=self.loads_config['E2'], Tg=0.35)  # 0.15g
        api.run_rs("e2dy", lcn=55, direction="Y", Ci=1.3, Cs=0.6, A=self.loads_config['E2'], Tg=0.25)  # 0.15g
        api.run_rs("e2dz", lcn=56, direction="Z", Ci=1.3, Cs=1.0, A=self.loads_config['E2'], Tg=0.35)  # 0.15g
        api.run_rs("e3dx", lcn=57, direction="X", Ci=1.3, Cs=1.0, A=self.loads_config['E3'], Tg=0.35)  # 0.20g
        api.run_rs("e3dy", lcn=58, direction="Y", Ci=1.3, Cs=0.6, A=self.loads_config['E3'], Tg=0.25)  # 0.20g
        api.run_rs("e3dz", lcn=59, direction="Z", Ci=1.3, Cs=1.0, A=self.loads_config['E3'], Tg=0.35)  # 0.20g
        api.run_rs("e4dx", lcn=61, direction="X", Ci=1.3, Cs=1.0, A=self.loads_config['E4'], Tg=0.35)  # 0.30g
        api.run_rs("e4dy", lcn=62, direction="Y", Ci=1.3, Cs=0.7, A=self.loads_config['E4'], Tg=0.25)  # 0.30g
        api.run_rs("e4dz", lcn=63, direction="Z", Ci=1.3, Cs=1.0, A=self.loads_config['E4'], Tg=0.35)  # 0.30g
        api.run_rs("e5dx", lcn=64, direction="X", Ci=1.3, Cs=1.0, A=self.loads_config['E5'], Tg=0.35)  # 0.40g
        api.run_rs("e5dy", lcn=65, direction="Y", Ci=1.3, Cs=0.7, A=self.loads_config['E5'], Tg=0.25)  # 0.40g
        api.run_rs("e5dz", lcn=66, direction="Z", Ci=1.3, Cs=1.0, A=self.loads_config['E5'], Tg=0.35)  # 0.40g
        api.run_rs("e6dx", lcn=67, direction="X", Ci=1.3, Cs=1.0, A=self.loads_config['E6'], Tg=0.35)  # 0.40g
        api.run_rs("e6dy", lcn=68, direction="Y", Ci=1.3, Cs=0.7, A=self.loads_config['E6'], Tg=0.25)  # 0.40g
        api.run_rs("e6dz", lcn=69, direction="Z", Ci=1.3, Cs=1.0, A=self.loads_config['E6'], Tg=0.35)  # 0.40g
        api.srss_rs('e1', lcn=11, lc_x=51, lc_y=52, lc_z=53)
        api.srss_rs('e2', lcn=12, lc_x=54, lc_y=55, lc_z=56)
        api.srss_rs('e3', lcn=13, lc_x=57, lc_y=58, lc_z=59)
        api.srss_rs('e4', lcn=14, lc_x=61, lc_y=62, lc_z=63)
        api.srss_rs('e5', lcn=15, lc_x=64, lc_y=65, lc_z=66)
        api.srss_rs('e6', lcn=16, lc_x=67, lc_y=68, lc_z=69)
        api.run_lcomb("ELS", conf={
            91: [(1, 1.0), (2, 1.0), (11, 1.0), ],
            92: [(1, 1.0), (2, 1.0), (12, 1.0), ],
            93: [(1, 1.0), (2, 1.0), (13, 1.0), ],
            94: [(1, 1.0), (2, 1.0), (14, 1.0), ],
            95: [(1, 1.0), (2, 1.0), (15, 1.0), ],
            96: [(1, 1.0), (2, 1.0), (16, 1.0), ],
        })
        config = {
            1: [6, 'Y', "RQuy"],
            2: [31, 'Z', "W1uz"],
            3: [32, 'Z', "W2uz"],
            4: [33, 'Z', "W3uz"],
            5: [34, 'Z', "W4uz"],
            6: [35, 'Z', "W5uz"],
            7: [36, 'Z', "W6uz"],
        }
        api.get_node_deformation(config)
        api.get_elem_forces(1, 81)
        api.get_elem_forces(1, 82)
        api.get_elem_forces(1, 83)
        api.get_elem_forces(1, 84)
        api.get_elem_forces(1, 85)
        api.get_elem_forces(1, 86)
        api.get_elem_forces(1, 91)
        api.get_elem_forces(1, 92)
        api.get_elem_forces(1, 93)
        api.get_elem_forces(1, 94)
        api.get_elem_forces(1, 95)
        api.get_elem_forces(1, 96)
        api.get_elem_forces(11, 81)
        api.get_elem_forces(11, 82)
        api.get_elem_forces(11, 83)
        api.get_elem_forces(11, 84)
        api.get_elem_forces(11, 85)
        api.get_elem_forces(11, 86)
        api.get_elem_forces(11, 91)
        api.get_elem_forces(11, 92)
        api.get_elem_forces(11, 93)
        api.get_elem_forces(11, 94)
        api.get_elem_forces(11, 95)
        api.get_elem_forces(11, 96)
        if self.config['clear']:
            api.clear()

    def configuration(self, **kwargs):
        self.config = {**kwargs}

    def loads(self, **kwargs):
        self.loads_config = {**kwargs}
