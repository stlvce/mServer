from math import pi

import matplotlib.pyplot as plt
import numpy as np

from state import state


# ==== Вспомогательные функции (заглушки, перепиши под свои) ====
def Fun_Dir_Pat(angle, width, side, mode):
    # Здесь должна быть твоя функция направленности
    return np.cos(angle) ** 2  # примерная модель


def Fun_dorUlabyC(angle, vid):
    # Заглушка — реальную зависимость подставь сам
    return -10 * (angle / (pi / 4)) ** 2


# ==== Пример параметров ====
Sqw = 2

kren = state.Tr.kren
tang = state.Tr.tang

DNA1 = np.array([50, 50])
DNA2 = np.array([50, 50])
f0 = np.array([10e9, 10e9])
AnglX_Prm = np.array([0, 0])
AnglZ_Prm = np.array([0, 0])
AnglX_Prd = np.array([0, 0])
AnglZ_Prd = np.array([0, 0])


def do_sign_imp():
    cMass = state.cMass
    state.Rs.tauimp = 10 * state.ns
    state.Rs.dtau = state.Rs.tauimp / 2

    # случайные данные для демонстрации
    Tr = {"Pos": np.random.randn(state.Rs.Nimp, 3)}

    Rs = {"AruType": 0, "dR": 1, "Logi": False}

    NLb = round(Sqw * state.Rs.tauimp / state.Rs.dtau)
    NLi = round(state.Rs.tauimp / state.Rs.dtau)

    # ==== Основной цикл ====
    ScosNN = []
    SsinNN = []

    for ChCnt in range(state.ChannelN):
        PdnaIzl = 81 / DNA1[ChCnt]
        PdnaPrm = 81 / DNA2[ChCnt]
        ScosN = np.zeros(NLb * (state.Rs.Nimp + 1))
        SsinN = np.zeros_like(ScosN)

        for FacCnt in range(state.FacetN):
            for ImpCnt in range(state.Rs.Nimp):
                X = cMass[0, FacCnt] - Tr["Pos"][ImpCnt, 0]
                Y = cMass[1, FacCnt] - Tr["Pos"][ImpCnt, 1]
                Z = cMass[2, FacCnt] - Tr["Pos"][ImpCnt, 2]

                R = np.sqrt(X**2 + Y**2 + Z**2)
                taur = 2 * R / state.c
                NLr = round(taur / state.Rs.dtau)

                AnX = np.arctan(Y / X) + cMass[9, FacCnt]
                AnZ = np.arctan(Y / Z) + cMass[10, FacCnt]

                Xeq = Y / np.tan(AnX)
                Zeq = Y / np.tan(AnZ)
                RsFeq = np.abs(Xeq + 1j * Zeq)
                alfaFac = -np.arctan(RsFeq / Y)

                aAntPrd = Fun_Dir_Pat(
                    alfaFac, np.deg2rad(DNA1[ChCnt] / 2), 0, state.vidDNA
                )
                aAntPrm = Fun_Dir_Pat(
                    alfaFac, np.deg2rad(DNA2[ChCnt] / 2), 0, state.vidDNA
                )

                Ador = Fun_Dir_Pat(alfaFac, cMass[8, FacCnt], 0, "G")
                Amp = np.sqrt(cMass[5, FacCnt] * aAntPrd * aAntPrm * Ador / (R**4))

                start_idx = NLr + ImpCnt * NLb
                end_idx = min(start_idx + NLi, len(ScosN))
                phase = -pi / 4 + 2 * pi * f0[ChCnt] * taur + cMass[3, FacCnt]

                SsinN[start_idx:end_idx] += Amp * np.sin(phase)
                ScosN[start_idx:end_idx] += Amp * np.cos(phase)

        # Нормировка
        NormK = np.max(np.abs(ScosN + 1j * SsinN))
        ScosN /= NormK
        SsinN /= NormK

        # Добавление шума
        NoiseC = np.random.randn(*ScosN.shape)
        NoiseS = np.random.randn(*SsinN.shape)
        SSpower = np.sum(np.abs(ScosN + 1j * SsinN))
        SSn = np.sum(np.abs(NoiseC + 1j * NoiseS))
        NormN = (SSpower / SSn) / (10 ** (int(state.Rs.snr) / 20))
        ScosN += NoiseC * NormN
        SsinN += NoiseS * NormN

        ScosNN.append(ScosN)
        SsinNN.append(SsinN)

    # ==== Визуализация ====
    ScosNN = np.array(ScosNN)
    SsinNN = np.array(SsinNN)
    signal_env = np.abs(ScosNN[0] + 1j * SsinNN[0])

    plt.figure(figsize=(10, 5))
    plt.plot(signal_env)
    plt.title("Отражённый сигнал (огибающая)")
    plt.xlabel("Относительная дальность (отсчёты)")
    plt.ylabel("Норм. амплитуда")
    plt.grid(True)
    plt.tight_layout()

    return ScosNN, SsinNN
