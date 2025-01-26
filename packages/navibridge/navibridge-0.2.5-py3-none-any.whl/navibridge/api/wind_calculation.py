import pint

ureg = pint.UnitRegistry()
Q_ = ureg.Quantity


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
