import numpy as np
import matplotlib.pyplot as plt
from typing import Any

import numpy as np
import matplotlib.pyplot as plt


def init_radar_image_processor_globals(
    globals: dict[str, Any] | None = None,
):
    """
    Инициализация параметров Rs и других значений по умолчанию.

    Args:
        globals (dict[str, Any]): Глобальные переменные
    """
    Rs = globals.get("Rs", {})
    Rs.setdefault("Rmin", 0.0)
    Rs.setdefault("Rmax", 1.0)
    Rs.setdefault("Log", False)
    Rs.setdefault("GB", 20)
    globals["Rs"] = Rs

    # Проверяем обязательные параметры
    required = ["dtau", "c", "H", "ChannelN", "AnglZ_Prm", "ScosNN", "SsinNN"]
    for param in required:
        if param not in globals:
            raise ValueError(f"В globals должен быть задан параметр '{param}'")

    # Инициализируем состояние
    globals["RLI"] = None
    globals.setdefault("test", {"canceling": 0, "h": {}, "fstep": [100, 100]})


def process_radar_image(globals: dict):
    """
    Основной метод обработки РЛ изображений.
    Результат сохраняется в globals['RLI'] и возвращается.

    Args:
        globals (dict[str, Any]): Глобальные переменные

    Returns:
        _Array[tuple[int, int], float64]
    """
    dtau = globals["dtau"]
    c = globals["c"]
    H = globals["H"]
    ChannelN = globals["ChannelN"]
    AnglZ_Prm = globals["AnglZ_Prm"]
    ScosNN = globals["ScosNN"]
    SsinNN = globals["SsinNN"]
    Rs = globals["Rs"]
    test = globals.get("test", {"canceling": 0})

    dR = dtau * c / 2
    RCmax = round((Rs["Rmax"] - Rs["Rmin"]) * H / dR)
    R = Rs["Rmin"] * H + RCmax * dR
    taur = 2 * R / c
    NLr = min(round(taur / dtau), RCmax)

    RLI = np.zeros((NLr, ChannelN))

    for ChCnt in range(1, ChannelN + 1):
        if test.get("canceling", 0):
            break
        ScosS = ScosNN[ChCnt - 1, :NLr]
        SsinS = SsinNN[ChCnt - 1, :NLr]
        SigX = ScosS + 1j * SsinS
        RLI[:NLr, ChCnt - 1] = np.abs(SigX)

    globals["RLI"] = RLI
    return RLI


def plot_radar_image_results(globals: dict):
    """
    Визуализация результатов обработки.

    Args:
        globals (dict[str, Any]): Глобальные переменные
    """
    if "RLI" not in globals or globals["RLI"] is None:
        raise ValueError("Сначала выполните process_radar_image()")

    RLI = globals["RLI"]
    dtau = globals["dtau"]
    c = globals["c"]
    Rs = globals["Rs"]
    AnglZ_Prm = globals["AnglZ_Prm"]

    dR = dtau * c / 2
    NLr = RLI.shape[0]
    Dal = dR * np.arange(NLr) + Rs["Rmin"] * globals["H"]

    fig = plt.figure(5)
    fig.canvas.manager.set_window_title("Дальность-азимут")

    if Rs["Log"]:
        plt.contour(AnglZ_Prm, Dal, np.log(RLI), Rs["GB"])
    else:
        plt.contour(AnglZ_Prm, Dal, RLI, Rs["GB"])

    plt.grid(True)
    plt.xlabel("Азимут (градусы)", fontsize=9)
    plt.ylabel("Дальность координат (м)", fontsize=9)
    plt.title("РЛ изображение", fontsize=9, fontweight="normal")
    plt.show()


def save_radar_image_results(globals: dict, filename: str = "RLIscan.npz"):
    """
    Сохранение результатов обработки в файл.

    Args:
        globals (dict[str, Any]): Глобальные переменные
        filename (str, optional): Имя файла. Defaults to "RLIscan.npz"
    """
    if "RLI" not in globals or globals["RLI"] is None:
        raise ValueError("Сначала выполните process_radar_image()")

    np.savez(filename, RLI=globals["RLI"], Rs=globals["Rs"])
