from typing import Any
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal.windows import hamming, blackman, hann


def init_radar_impulse_processor_globals(
    globals: dict[str, Any] | None = None,
):
    """
    Инициализация параметров и оконной функции в globals.
    Если параметры отсутствуют, задаются значения по умолчанию.

    Args:
        globals (dict[str, Any]): Глобальные переменные
    """
    Rs = globals.get("Rs", {})
    # Устанавливаем параметры по умолчанию, если отсутствуют
    Rs.setdefault("Rmin", 0.0)
    Rs.setdefault("Rmax", 1.0)
    Rs.setdefault("Log", False)
    Rs.setdefault("GB", 20)
    Rs.setdefault("Wnd", 0)  # 0 - нет окна, 1 - Хемминга, 2 - Блэкмана, 3 - Ханна
    globals["Rs"] = Rs

    Nimp = globals.get("Nimp")
    if Nimp is None:
        raise ValueError("В globals должен быть задан параметр 'Nimp'")

    # Инициализация оконной функции
    wnd_type = Rs["Wnd"]
    if wnd_type == 1:
        wnd_f = hamming(Nimp)
    elif wnd_type == 2:
        wnd_f = blackman(Nimp)
    elif wnd_type == 3:
        wnd_f = hann(Nimp)
    else:
        wnd_f = np.ones(Nimp)
    globals["wnd_f"] = wnd_f


def process_radar_impulse(globals: dict):
    """
    Основной метод обработки импульсных РЛ данных.
    Возвращает массив RLI и сохраняет его в globals.

    Args:
        globals (dict[str, Any]): Глобальные переменные

    Returns:
        _Array[tuple[int, int, int], float64]
    """
    dtau = globals["dtau"]
    c = globals["c"]
    H = globals["H"] if globals["H"] > 0 else 10.0
    ChannelN = globals["ChannelN"]
    Nimp = globals["Nimp"]
    tauimp = globals["tauimp"]
    Sqw = globals["Sqw"]
    Timp = globals["Timp"]
    ScosNN = globals["ScosNN"]
    SsinNN = globals["SsinNN"]
    Rs = globals["Rs"]
    test = globals.get("test", {"canceling": False, "h": {}, "fstep": [100, 100]})
    wnd_f = globals.get("wnd_f", np.ones(Nimp))

    dR = dtau * c
    NLi = round(tauimp / dtau)
    NLb = round(Sqw * tauimp / dtau)
    RCmax = round((Rs["Rmax"] - Rs["Rmin"]) * H / dR)

    RLI = np.zeros((ChannelN, RCmax, Nimp))

    for ChCnt in range(ChannelN):
        if test["canceling"]:
            break
        for RCounter in range(RCmax):
            if test["canceling"]:
                break

            R = Rs["Rmin"] * H + (RCounter + 1) * dR
            taur = 2 * R / c
            NLr = round(taur / dtau)

            indices = np.minimum(
                1 + NLr + np.arange(Nimp) * NLb, ScosNN.shape[1] - 1
            ).astype(int)
            ScosS = ScosNN[ChCnt, indices]
            SsinS = SsinNN[ChCnt, indices]
            SigX = ScosS + 1j * SsinS

            if Rs["Wnd"] > 0:
                SigX = SigX * wnd_f

            RLI[ChCnt, RCounter, :] = np.abs(np.fft.fft(SigX))

    globals["RLI"] = RLI
    return RLI


def plot_radar_impulse_results(globals: dict):
    """
    Визуализация результатов обработки.

    Args:
        globals (dict[str, Any]): Глобальные переменные
    """
    if "RLI" not in globals or globals["RLI"] is None:
        raise ValueError("Сначала выполните process_radar_impulse()")

    RLI = globals["RLI"]
    dtau = globals["dtau"]
    c = globals["c"]
    H = globals["H"]
    Nimp = globals["Nimp"]
    Timp = globals["Timp"]
    Rs = globals["Rs"]
    ChannelN = globals["ChannelN"]

    dR = dtau * c
    Dal = dR * np.arange(1, RLI.shape[1] + 1) + Rs["Rmin"] * H
    Dop = np.arange(0.5 - Nimp / 2, Nimp / 2 - 0.5 + 1) / (Timp * Nimp)

    fig = plt.figure(figsize=(15, 5))
    fig.canvas.manager.set_window_title("Дальность-доплер")

    ChCntMax = min(3, ChannelN)
    ch_indices = np.linspace(0, ChannelN - 1, ChCntMax, dtype=int)

    for i, ChCnt in enumerate(ch_indices):
        RLI1 = RLI[ChCnt, :, :]
        RLI1f = np.roll(RLI1, shift=RLI1.shape[1] // 2, axis=1)
        RLI1f = np.fliplr(RLI1f)

        plt.subplot(1, ChCntMax, i + 1)

        if Rs["Log"]:
            plt.contour(Dop * 1e-3, Dal, np.log(RLI1f), Rs["GB"])
        else:
            plt.imshow(
                RLI1f,
                extent=[Dop[0] * 1e-3, Dop[-1] * 1e-3, Dal[0], Dal[-1]],
                aspect="auto",
            )

        plt.grid(True)
        plt.xlabel("Доплер (кГц)", fontsize=9)
        plt.ylabel("Дальность координат (м)", fontsize=9)
        plt.title(f"Канал {ChCnt + 1}", fontsize=9, fontweight="normal")

    if ChannelN == 1:
        plt.title("РЛ изображение", fontsize=9, fontweight="normal")
        plt.colorbar()

    plt.tight_layout()
    plt.show()


def save_radar_impulse_results(globals: dict, filename: str = "RLIimp.npz"):
    """
    Сохранение результатов обработки в файл.

    Args:
        globals (dict[str, Any]): Глобальные переменные
        filename (str, optional): Имя файла. Defaults to "RLIimp.npz"
    """
    if "RLI" not in globals or globals["RLI"] is None:
        raise ValueError("Сначала выполните process_radar_impulse()")

    np.savez(filename, RLI=globals["RLI"], Rs=globals["Rs"])
