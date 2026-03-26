import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import io
from math import pi


# ====== заглушки вспомогательных функций (реализуй свои) ======
def Fun_Dir_Pat(angle, width, side, mode):
    return np.cos(angle) ** 2


def Fun_dorUlabyC(angle, vid):
    return -10 * (angle / (pi / 4)) ** 2


# ====== пример параметров (должны быть заданы извне) ======
test = {"canceling": 0, "pF": 1, "pN": 3}
ChannelN = 2
FacetN = 5
Nimp = 10
Tm = 1e-4
dtau = 1e-7
c = 3e8
Wd = 1e6
snr = 20
vidDNA = "SC1"
vidDOR = ["G"] * FacetN
DNA1 = np.array([30, 30])
DNA2 = np.array([30, 30])
f0 = np.array([10e9, 10e9])
AnglX_Prm = np.zeros(ChannelN)
AnglZ_Prm = np.zeros(ChannelN)
AnglX_Prd = np.zeros(ChannelN)
AnglZ_Prd = np.zeros(ChannelN)
kren = 0
tang = 0
cMass = np.random.rand(14, FacetN)
Tr = {"Pos": np.random.randn(Nimp, 3), "Tm": np.linspace(1, Nimp, Nimp)}

# ====== расчёт ======
perc_mem = -1
Ni = round(Tm / dtau)
SigCN = np.zeros((ChannelN, Nimp, Ni))
SigSN = np.zeros_like(SigCN)


def do_sign_fm():
    for ChCnt in range(ChannelN):
        if test["canceling"]:
            break

        PdnaIzl = 81 / DNA1[ChCnt]
        PdnaPrm = 81 / DNA2[ChCnt]
        SigS = np.zeros((Nimp, Ni))
        SigC = np.zeros_like(SigS)

        for FacCnt in range(FacetN):
            perc = round(100 * (FacCnt + ChCnt * FacetN) / (FacetN * ChannelN))
            if perc > perc_mem:
                perc_mem = perc
                print(f"Progress: {perc}%")

            for ImpCnt in range(Nimp):
                X = cMass[0, FacCnt] - Tr["Pos"][ImpCnt, 0]
                Y = cMass[1, FacCnt] - Tr["Pos"][ImpCnt, 1]
                Z = cMass[2, FacCnt] - Tr["Pos"][ImpCnt, 2]
                R = np.sqrt(X**2 + Y**2 + Z**2)
                taur = 2 * R / c

                AnX = np.arctan(Y / X) + np.deg2rad(cMass[9, FacCnt])
                AnZ = np.arctan(Y / Z) + np.deg2rad(cMass[10, FacCnt])
                Xeq = Y / np.tan(AnX)
                Zeq = Y / np.tan(AnZ)
                RsFeq = np.abs(Xeq + 1j * Zeq)
                alfaFac = np.arctan(RsFeq / Y)

                Ya1 = np.abs(Y)
                Xa1 = Ya1 * np.tan(np.deg2rad(AnglX_Prm[ChCnt] + kren))
                Za1 = Ya1 * np.tan(np.deg2rad(AnglZ_Prm[ChCnt] + tang))
                alfaAnt_Prm = np.arccos(
                    (Y * Ya1 + X * Xa1 + Z * Za1)
                    / (R * np.sqrt(Ya1**2 + Xa1**2 + Za1**2))
                )

                Ya2 = np.abs(Y)
                Xa2 = Ya2 * np.tan(np.deg2rad(AnglX_Prd[ChCnt] + kren))
                Za2 = Ya2 * np.tan(np.deg2rad(AnglZ_Prd[ChCnt] + tang))
                alfaAnt_Prd = np.arccos(
                    (Y * Ya2 + X * Xa2 + Z * Za2)
                    / (R * np.sqrt(Ya2**2 + Xa2**2 + Za2**2))
                )

                aAntPrd = Fun_Dir_Pat(
                    alfaAnt_Prd - pi, np.deg2rad(DNA1[ChCnt] / 2), 0, vidDNA
                )
                aAntPrm = Fun_Dir_Pat(
                    alfaAnt_Prm - pi, np.deg2rad(DNA2[ChCnt] / 2), 0, vidDNA
                )

                if vidDOR[int(abs(cMass[4, FacCnt]))] == "G":
                    Ador = Fun_Dir_Pat(alfaFac, cMass[8, FacCnt], 0, "G")
                else:
                    Ador = 10 ** (
                        Fun_dorUlabyC(alfaFac, vidDOR[int(abs(cMass[4, FacCnt]))]) / 10
                    )

                Amp = np.sqrt(cMass[5, FacCnt] * aAntPrd * aAntPrm * Ador / (R**4))
                Fb = 2 * Wd * R / (c * Tr["Tm"][ImpCnt])

                tt = np.arange(Ni)
                fc = f0[ChCnt] + Wd * (tt / Ni - 0.5)
                Arg = (
                    2 * pi * Fb * Tr["Tm"][ImpCnt] * tt / Ni + 2 * pi * f0[ChCnt] * taur
                )
                SigFc = Amp * np.cos(Arg + cMass[3, FacCnt])
                SigFs = Amp * np.sin(Arg + cMass[3, FacCnt])

                SigS[ImpCnt, :] += SigFs
                SigC[ImpCnt, :] += SigFc

        SigC[np.isnan(SigC)] = 0
        SigS[np.isnan(SigS)] = 0

        SSpower = np.sum(np.abs(SigC + 1j * SigS))
        NoiseC = np.random.randn(Nimp, Ni)
        NoiseS = np.random.randn(Nimp, Ni)
        SSn = np.sum(np.abs(NoiseC + 1j * NoiseS))
        NormN = (SSpower / SSn) / (10 ** (snr / 20))
        SigCN[ChCnt, :, :] = SigC + NoiseC * NormN
        SigSN[ChCnt, :, :] = SigS + NoiseS * NormN

    # ====== построение графика ======
    ii_start = int(1 + Ni * (test["pF"] - 1))
    ii_end = int(min(round(Ni * test["pN"]), SigCN.shape[2]))
    ii = np.arange(ii_start, ii_end)
    signal_env = np.abs(SigCN[0, 0, ii] + 1j * SigSN[0, 0, ii]) + 1e-10

    plt.figure(figsize=(10, 5))
    plt.plot(ii, signal_env, color="blue")
    plt.title("Отражённый сигнал")
    plt.xlabel("Относительная дальность (м)")
    plt.ylabel("Норм. амплитуда² (В²)")
    plt.grid(True)
    plt.tight_layout()

    # ====== сохранить график в BMP ======
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=150)
    plt.close()
    buf.seek(0)
    Image.open(buf).convert("RGB").save("signal2.bmp")
    print("✅ График сохранён как signal2.bmp")

    return SigSN
