from math import pi

import numpy as np

from helpers.save_bmp import save_fig_as_bmp
from state import state


def _fun_dir_pat(
    angle: np.ndarray, half_width: float, side: int, mode: str
) -> np.ndarray:
    a = np.atleast_1d(np.asarray(angle, dtype=float))
    if half_width == 0:
        return np.ones_like(a)
    x = a / half_width
    if mode == "G":
        y = np.exp(-(x**2) * np.log(2))
    elif mode.startswith("SC"):
        pi_x = np.pi * x
        sinc = np.where(np.abs(pi_x) < 1e-9, 1.0, np.sin(pi_x) / pi_x)
        y = sinc**2
    else:
        y = np.cos(np.clip(a, -np.pi / 2, np.pi / 2)) ** 2
    result = np.abs(y)
    if side > 0:
        result[a < 0] = 0.0
    elif side < 0:
        result[a > 0] = 0.0
    return result


def _fun_dor_ulaby_c(angle: float, vid: str) -> float:
    return -10.0 * (angle / (np.pi / 4)) ** 2


def _get_vid_dor(surface_type: int) -> str:
    mapping: dict[int, str] = {
        1: state.vidDOR1,
        2: state.vidDOR2,
        7: state.vidDOR7,
    }
    return mapping.get(int(surface_type), "G")


def do_sign_fm():
    """
    Модель сигнала для ЛЧМ радара с СА.
    Аналог Do_SignFM.m.
    Возвращает (SigSN, SigCN, Ni).
    """
    Rs = state.Rs
    Tr = state.Tr
    cMass = state.cMass

    n_ch = max(int(state.ChannelN), 1)
    FacetN = int(state.FacetN)
    Nimp = int(Rs.Nimp)
    dtau = float(Rs.dtau)
    Tm = float(Rs.Tm)
    snr_lin = float(Rs.snr)
    Wd = float(state.Wd)

    Ni = round(Tm / dtau)  # отсчётов в ЛЧМ-импульсе

    DNA1_arr = [float(state.DNA1[0])] * n_ch
    DNA2_arr = [float(state.DNA2[0])] * n_ch
    AnglX_Prm = [float(state.AnglX_Prm[0])] * n_ch
    AnglZ_Prm = [float(state.AnglZ_Prm[0])] * n_ch
    AnglX_Prd = [float(state.AnglX_Prd[0])] * n_ch
    AnglZ_Prd = [float(state.AnglZ_Prd[0])] * n_ch
    f0_arr = [
        float(v)
        for v in (state.f0[:n_ch] if len(state.f0) >= n_ch else [state.f0[0]] * n_ch)
    ]

    kren = float(Tr.kren)
    tang = float(Tr.tang)

    Tr_Tm = Tr.Tm  # время каждого импульса (массив длиной Nimp)

    SigCN = np.zeros((n_ch, Nimp, Ni))
    SigSN = np.zeros_like(SigCN)

    tt = np.arange(Ni)  # общий для всех итераций (не зависит от FacCnt/ImpCnt)

    for ChCnt in range(n_ch):
        if state.test.canceling:
            break

        SigS = np.zeros((Nimp, Ni))
        SigC = np.zeros_like(SigS)

        for FacCnt in range(FacetN):
            if state.test.canceling:
                break

            perc = round(100 * (FacCnt + ChCnt * FacetN) / (FacetN * n_ch))
            # TODO убрать комментарий
            # print(f"Канал {ChCnt + 1}/{n_ch}, фацет {FacCnt + 1}/{FacetN} ({perc}%)")

            for ImpCnt in range(Nimp):
                X = cMass[0, FacCnt] - Tr.Pos[ImpCnt, 0]
                Y = cMass[1, FacCnt] - Tr.Pos[ImpCnt, 1]
                Z = cMass[2, FacCnt] - Tr.Pos[ImpCnt, 2]

                R = np.sqrt(X**2 + Y**2 + Z**2)
                if R < 1e-9:
                    continue

                taur = 2.0 * R / state.c

                AnX = np.arctan2(Y, X) + cMass[9, FacCnt]
                AnZ = np.arctan2(Y, Z) + cMass[10, FacCnt]
                Xeq = Y / (np.tan(AnX) if abs(np.tan(AnX)) > 1e-9 else 1e-9)
                Zeq = Y / (np.tan(AnZ) if abs(np.tan(AnZ)) > 1e-9 else 1e-9)
                RsFeq = abs(Xeq + 1j * Zeq)
                alfaFac = -np.arctan2(RsFeq, abs(Y))

                Ya1 = abs(Y)
                Xa1 = Ya1 * np.tan(np.deg2rad(AnglX_Prm[ChCnt] + kren))
                Za1 = Ya1 * np.tan(np.deg2rad(AnglZ_Prm[ChCnt] + tang))
                norm1 = np.sqrt(Ya1**2 + Xa1**2 + Za1**2)
                cos_prm = -(Y * Ya1 + X * Xa1 + Z * Za1) / (R * norm1 + 1e-30)
                alfaAnt_Prm = np.arccos(np.clip(cos_prm, -1.0, 1.0))

                Ya2 = abs(Y)
                Xa2 = Ya2 * np.tan(np.deg2rad(AnglX_Prd[ChCnt] + kren))
                Za2 = Ya2 * np.tan(np.deg2rad(AnglZ_Prd[ChCnt] + tang))
                norm2 = np.sqrt(Ya2**2 + Xa2**2 + Za2**2)
                cos_prd = -(Y * Ya2 + X * Xa2 + Z * Za2) / (R * norm2 + 1e-30)
                alfaAnt_Prd = np.arccos(np.clip(cos_prd, -1.0, 1.0))

                aAntPrd = float(
                    _fun_dir_pat(
                        alfaAnt_Prd, np.deg2rad(DNA1_arr[ChCnt] / 2), 0, state.vidDNA
                    )[0]
                )
                aAntPrm = float(
                    _fun_dir_pat(
                        alfaAnt_Prm, np.deg2rad(DNA2_arr[ChCnt] / 2), 0, state.vidDNA
                    )[0]
                )
                if np.isnan(aAntPrd):
                    aAntPrd = 0.0
                if np.isnan(aAntPrm):
                    aAntPrm = 0.0

                vid_dor = _get_vid_dor(int(cMass[4, FacCnt]))
                if vid_dor == "G":
                    Ador = float(_fun_dir_pat(alfaFac, cMass[8, FacCnt], 0, "G")[0])
                else:
                    Ador = float(10.0 ** (_fun_dor_ulaby_c(alfaFac, vid_dor) / 10.0))

                Amp = np.sqrt(
                    cMass[5, FacCnt] * float(aAntPrd) * float(aAntPrm) * Ador / (R**4)
                )

                # Доплеровская биение-частота
                Tm_i = float(Tr_Tm[ImpCnt]) if len(Tr_Tm) > ImpCnt else Tm
                Fb = 2.0 * Wd * R / (state.c * Tm_i) if Tm_i != 0 else 0.0

                Arg = 2.0 * pi * Fb * Tm_i * tt / Ni + 2.0 * pi * f0_arr[ChCnt] * taur
                SigC[ImpCnt, :] += Amp * np.cos(Arg + cMass[3, FacCnt])
                SigS[ImpCnt, :] += Amp * np.sin(Arg + cMass[3, FacCnt])

        SigC[np.isnan(SigC)] = 0.0
        SigS[np.isnan(SigS)] = 0.0

        SSpower = np.sum(np.abs(SigC + 1j * SigS))
        NoiseC = np.random.randn(Nimp, Ni)
        NoiseS = np.random.randn(Nimp, Ni)
        SSn = np.sum(np.abs(NoiseC + 1j * NoiseS))
        NormN = (SSpower / SSn) / (10 ** (snr_lin / 20)) if SSn > 0 else 0.0
        SigCN[ChCnt] = SigC + NoiseC * NormN
        SigSN[ChCnt] = SigS + NoiseS * NormN

    # Визуализация (аналог figure(5) в MATLAB)
    pF = max(state.test.pF, 1)
    pN = max(state.test.pN, 1)
    ii_start = int(Ni * (pF - 1))
    ii_end = int(min(round(Ni * pN), SigCN.shape[2]))
    ii = np.arange(ii_start, ii_end)

    import matplotlib.pyplot as plt

    signal_env = np.abs(SigCN[0, 0, ii] + 1j * SigSN[0, 0, ii]) + 1e-10

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(ii, signal_env, color="blue")
    ax.set_title("Отражённый ЛЧМ сигнал", fontsize=9, fontweight="normal")
    ax.set_xlabel("Отсчёты дальности", fontsize=9)
    ax.set_ylabel("Норм. амплитуда (В)", fontsize=9)
    ax.grid(True)
    ax.autoscale(axis="both", tight=True)
    plt.tight_layout()
    save_fig_as_bmp("resultFig5.bmp")

    return SigSN, SigCN, Ni
