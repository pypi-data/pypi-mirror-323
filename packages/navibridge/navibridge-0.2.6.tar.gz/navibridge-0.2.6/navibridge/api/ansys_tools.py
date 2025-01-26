import numpy as np

def PrintSPD(Ts, S, file):
    with open(file, "w+") as fid:
        fid.write("*UNIT,GRAV\n")
        fid.write("*TYPE,ACCEL\n")
        fid.write("*Data\n")
        for i, t in enumerate(Ts):
            fid.write("%.4E,%.6f\n" % (t, S[i]))


def GetS(Smax, Tg, T):
    T0 = 0.1
    if T < T0:
        return Smax * (0.6 * T / T0 + 0.4)
    elif T < Tg:
        return Smax
    else:
        return Smax * (Tg / T)


def GetDES(Smax, Tg, Ta=0.0, Tb=10.0, Tstep=0.01):
    Tlist = np.linspace(Ta, Tb, int(np.round((Tb - Ta) / Tstep + 1)))
    Slist = [GetS(Smax, Tg, ti) for ti in Tlist]
    return [Tlist.tolist(), Slist]


def GetSmax(Ci, Cs, Cd, A):
    return 2.5 * Ci * Cs * Cd * A


def GetCd(xi):
    return max(1 + (0.05 - xi) / (0.08 + 1.6 * xi), 0.55)


if __name__ == "__main__":
    Cd0 = GetCd(0.03)
    print("Cd=%.4f" % Cd0)
    Smax_E1x = GetSmax(0.34, 1.0, Cd0, 0.2)
    Smax_E1z = GetSmax(0.34, 0.6, Cd0, 0.2)
    Smax_E2x = GetSmax(1.3, 1.0, Cd0, 0.2)
    Smax_E2z = GetSmax(1.3, 0.6, Cd0, 0.2)
    print("Smax_E1x = %.4f" % Smax_E1x)
    print("Smax_E1z = %.4f" % Smax_E1z)
    print("Smax_E2x = %.4f" % Smax_E2x)
    print("Smax_E2z = %.4f" % Smax_E2z)
    DES_E1x = GetDES(Smax_E1x, 0.45)
    DES_E1z = GetDES(Smax_E1z, 0.45)
    DES_E2x = GetDES(Smax_E2x, 0.45)
    DES_E2z = GetDES(Smax_E2z, 0.45)

    PrintSPD(DES_E1x[0], DES_E1x[1], "../../bin/out/E1水平设计反应谱.spd")
    PrintSPD(DES_E2x[0], DES_E2x[1], "../../bin/out/E2水平设计反应谱.spd")
