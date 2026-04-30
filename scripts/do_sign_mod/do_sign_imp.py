import matplotlib.pyplot as plt
import numpy as np

from state import state

# ─────────────────────────────────────────────────────────────────────────────
# Вспомогательные функции
# ─────────────────────────────────────────────────────────────────────────────


def _fun_dir_pat(
    angle: np.ndarray, half_width: float, side: int, mode: str
) -> np.ndarray:
    """
    Аппроксимация ДНА. Аналог Fun_Dir_Pat.m.
    angle      — угловое отклонение от оси, рад
    half_width — полуширина ДНА, рад
    side       — 0: полная; >0: правая; <0: левая
    mode       — 'SC...' sinc², 'G' Гауссова, иначе cos²
    """
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
    """
    Коэффициент обратного рассеяния по модели Ulaby (дБ). Аналог Fun_dorUlabyC.m.
    """
    # TODO: реализовать реальные кривые Ulaby для каждого типа поверхности
    return -10.0 * (angle / (np.pi / 4)) ** 2


def _get_vid_dor(surface_type: int) -> str:
    """Возвращает тип ДОР по коду типа поверхности из cMass[4,FacCnt]."""
    mapping: dict[int, str] = {
        1: state.vidDOR1,
        2: state.vidDOR2,
        7: state.vidDOR7,
    }
    return mapping.get(int(surface_type), "G")


# ─────────────────────────────────────────────────────────────────────────────
# Основная функция
# ─────────────────────────────────────────────────────────────────────────────


def do_sign_imp():
    """
    Модель сигнала для импульсного радара с СА.
    Аналог Do_SignImp.m.
    Возвращает (ScosNN, SsinNN) — квадратурные составляющие для всех каналов.
    """
    Rs = state.Rs
    Tr = state.Tr
    cMass = state.cMass

    n_ch = max(int(state.ChannelN), 1)
    FacetN = int(state.FacetN)
    Nimp = int(Rs.Nimp)
    dtau = float(Rs.dtau)
    tauimp = float(Rs.tauimp)
    snr_lin = float(Rs.snr)
    Sqw = int(state.Sqw) or 2  # защита от нуля: минимум 2

    NLb = round(Sqw * tauimp / dtau)  # отсчётов в периоде следования
    NLi = round(tauimp / dtau)  # отсчётов в импульсе

    # Реплицируем скалярные параметры по каналам (state хранит один набор)
    # DNA может быть комплексным (real=ширина_X, imag=ширина_Z) — берём real
    DNA1_arr = [float(np.real(complex(state.DNA1[0])))] * n_ch
    DNA2_arr = [float(np.real(complex(state.DNA2[0])))] * n_ch
    AnglX_Prm = [float(np.real(complex(state.AnglX_Prm[0])))] * n_ch
    AnglZ_Prm = [float(np.real(complex(state.AnglZ_Prm[0])))] * n_ch
    AnglX_Prd = [float(np.real(complex(state.AnglX_Prd[0])))] * n_ch
    AnglZ_Prd = [float(np.real(complex(state.AnglZ_Prd[0])))] * n_ch
    f0_arr = [
        float(v)
        for v in (state.f0[:n_ch] if len(state.f0) >= n_ch else [state.f0[0]] * n_ch)
    ]

    kren = float(Tr.kren)  # крен ЛА, градусы
    tang = float(Tr.tang)  # тангаж ЛА, градусы

    # Буфер под результат — размер с запасом для максимальной задержки + все импульсы
    buf_len = NLb * (Nimp + 2)

    ScosNN_list: list[np.ndarray] = []
    SsinNN_list: list[np.ndarray] = []

    for ChCnt in range(n_ch):
        if state.test.canceling:
            break

        ScosN = np.zeros(buf_len)
        SsinN = np.zeros(buf_len)

        for FacCnt in range(FacetN):
            if state.test.canceling:
                break

            # Прогресс
            perc = round(100 * (FacCnt + ChCnt * FacetN) / (FacetN * n_ch))
            print(f"Канал {ChCnt + 1}/{n_ch}, фацет {FacCnt + 1}/{FacetN} ({perc}%)")

            for ImpCnt in range(Nimp):
                # Координаты фацета относительно ЛА
                X = cMass[0, FacCnt] - Tr.Pos[ImpCnt, 0]
                Y = cMass[1, FacCnt] - Tr.Pos[ImpCnt, 1]
                Z = cMass[2, FacCnt] - Tr.Pos[ImpCnt, 2]

                R = np.sqrt(X**2 + Y**2 + Z**2)
                if R < 1e-9:
                    continue

                taur = 2.0 * R / state.c
                NLr = round(taur / dtau)

                # Углы визирования фацета с учётом его собственного наклона
                AnX = np.arctan2(Y, X) + cMass[9, FacCnt]  # по оси X
                AnZ = np.arctan2(Y, Z) + cMass[10, FacCnt]  # по оси Z

                # Эквивалентные координаты с учётом наклона фацета
                Xeq = Y / (np.tan(AnX) if abs(np.tan(AnX)) > 1e-9 else 1e-9)
                Zeq = Y / (np.tan(AnZ) if abs(np.tan(AnZ)) > 1e-9 else 1e-9)
                RsFeq = abs(Xeq + 1j * Zeq)
                alfaFac = -np.arctan2(RsFeq, abs(Y))  # угол визирования ДОР

                # ── Угол визирования от приёмной антенны ──
                Ya1 = abs(Y)
                Xa1 = Ya1 * np.tan(np.deg2rad(AnglX_Prm[ChCnt] + kren))
                Za1 = Ya1 * np.tan(np.deg2rad(AnglZ_Prm[ChCnt] + tang))
                norm1 = np.sqrt(Ya1**2 + Xa1**2 + Za1**2)
                cos_prm = -(Y * Ya1 + X * Xa1 + Z * Za1) / (R * norm1 + 1e-30)
                alfaAnt_Prm = np.arccos(np.clip(cos_prm, -1.0, 1.0))

                # ── Угол визирования от передающей антенны ──
                Ya2 = abs(Y)
                Xa2 = Ya2 * np.tan(np.deg2rad(AnglX_Prd[ChCnt] + kren))
                Za2 = Ya2 * np.tan(np.deg2rad(AnglZ_Prd[ChCnt] + tang))
                norm2 = np.sqrt(Ya2**2 + Xa2**2 + Za2**2)
                cos_prd = -(Y * Ya2 + X * Xa2 + Z * Za2) / (R * norm2 + 1e-30)
                alfaAnt_Prd = np.arccos(np.clip(cos_prd, -1.0, 1.0))

                # ── Коэффициенты ДНА ──
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

                # ── Коэффициент ДОР ──
                vid_dor = _get_vid_dor(int(cMass[4, FacCnt]))
                if vid_dor == "G":
                    Ador = float(_fun_dir_pat(alfaFac, cMass[8, FacCnt], 0, "G")[0])
                else:
                    Ador = float(10.0 ** (_fun_dor_ulaby_c(alfaFac, vid_dor) / 10.0))

                # Запомним коэффициенты для первого импульса и первого канала
                if ImpCnt == 0 and ChCnt == 0:
                    cMass[11, FacCnt] = np.sqrt(aAntPrd * aAntPrm)
                    cMass[12, FacCnt] = Ador

                # ── Амплитуда ──
                Amp = np.sqrt(cMass[5, FacCnt] * aAntPrd * aAntPrm * Ador / (R**4))
                if Rs.AruType > 0:
                    Amp *= R**Rs.AruType

                # ── Формирование квадратур ──
                start = NLr + ImpCnt * NLb
                end = min(start + NLi + 1, buf_len)
                if start >= buf_len:
                    continue

                phase = -np.pi / 4 + 2 * np.pi * f0_arr[ChCnt] * taur + cMass[3, FacCnt]
                ScosN[start:end] += Amp * np.cos(phase)
                SsinN[start:end] += Amp * np.sin(phase)

                # Пауза (явное обнуление, как в MATLAB)
                p_start = min(start + NLi + 1, buf_len)
                p_end = min(NLr + NLb + ImpCnt * NLb, buf_len)
                if p_start < p_end:
                    ScosN[p_start:p_end] = 0.0
                    SsinN[p_start:p_end] = 0.0

        # ── Нормировка ──
        NormK = np.max(np.abs(ScosN + 1j * SsinN))
        if NormK > 0:
            ScosN /= NormK
            SsinN /= NormK

        # ── Добавление шума ──
        Cimp = np.sum(np.sign(np.abs(ScosN)))  # число ненулевых отсчётов
        Cimp = max(Cimp, 1)
        SSpower = np.sum(np.abs(ScosN + 1j * SsinN))
        NoiseC = np.random.randn(*ScosN.shape)
        NoiseS = np.random.randn(*SsinN.shape)
        SSn = np.sum(np.abs(NoiseC + 1j * NoiseS))
        NormN = (SSpower / SSn) / (10 ** (snr_lin / 20)) * len(ScosN) / Cimp
        ScosN += NoiseC * NormN
        SsinN += NoiseS * NormN

        ScosNN_list.append(ScosN)
        SsinNN_list.append(SsinN)

    ScosNN = np.array(ScosNN_list)
    SsinNN = np.array(SsinNN_list)

    # ── Визуализация (аналог figure(4) в MATLAB) ──
    pF = max(state.test.pF, 1)
    pN = max(state.test.pN, 1)
    ii = np.arange(NLb * (pF - 1), min(round(NLb * pN), ScosNN.shape[1]))
    x_m = ii * Rs.dR / 2  # дальность, м

    envelope = np.abs(ScosNN[0, ii] + 1j * SsinNN[0, ii]) + 1e-10

    fig, ax = plt.subplots(figsize=(6, 3))
    if Rs.Logi:
        ax.semilogy(x_m, envelope)
    else:
        ax.plot(x_m, envelope)
    ax.set_title("Отражённый сигнал", fontsize=9, fontweight="normal")
    ax.set_xlabel("Относительная (от 1-го имп.запроса) дальность (м)", fontsize=9)
    ax.set_ylabel("Норм. амплитуда² (В²)", fontsize=9)
    ax.grid(True, which="both")
    ax.autoscale(axis="both", tight=True)
    plt.tight_layout()

    return ScosNN, SsinNN
