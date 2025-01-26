import os
from abc import ABCMeta, abstractmethod

import pint

ureg = pint.UnitRegistry()
Q_ = ureg.Quantity


class BaseAPI(metaclass=ABCMeta):
    def __init__(self, project, root_path, init=True):
        # self.cwd = ""
        self.options = {}
        self.fem: 'FEM' = None
        self.project_name = project
        wdr = os.path.join(root_path, self.project_name)
        self.cwd = os.path.abspath(wdr)
        self.res_dir = os.path.join(os.path.abspath(root_path), f'{project}_result.txt')
        self.init = init
        self.loads = {}

    def config(self, **kwargs):
        self.options = {**kwargs}

    def load_config(self, **kwargs):
        self.loads = {**kwargs}

    def write_dxf(self, dxf_file):
        import ezdxf
        from ezdxf.lldxf.const import DXFTableEntryError
        # 创建一个新的 DXF 文档
        doc = ezdxf.new(dxfversion='R2010')
        for s in self.fem.sect_list.keys():
            sec = self.fem.sect_list[s]
            try:
                doc.layers.add(name=f"{sec.name}", color=sec.id)
            except DXFTableEntryError:
                continue
        # 获取模型空间（用于绘制图形）
        msp = doc.modelspace()
        for ek in self.fem.elem_list.keys():
            ele = self.fem.elem_list[ek]
            # 绘制一条空间直线，指定起点和终点，并设置图层为 "Layer1"
            start_point = [v * 1e-3 for v in ele.nlist[0].vec.xyz]  # 起点坐标
            end_point = [v * 1e-3 for v in ele.nlist[1].vec.xyz]  # 终点坐标
            secn = self.fem.sect_list[ele.secn].name
            msp.add_line(start_point, end_point, dxfattribs={'layer': secn})

        # 保存为一个新的 DXF 文件
        doc.saveas(os.path.join(self.cwd, dxf_file))

    @abstractmethod
    def clear(self):
        pass

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
