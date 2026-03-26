from typing import Any
import numpy as np
import matplotlib.pyplot as plt
import io
from PIL import Image
import win32clipboard


def copy_image_to_clipboard(img: Image.Image):
    # Сохраняем изображение в BMP-поток
    output = io.BytesIO()
    img.convert("RGB").save(output, "BMP")
    data = output.getvalue()[14:]  # Убираем заголовок BMP (14 байт)
    output.close()

    # Копируем в буфер обмена (Windows API)
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
    win32clipboard.CloseClipboard()


def process_fm_radar(
    globals: dict[str, Any] = {},
):
    """
    Обработка FM-радара

    Выполняет двумерное преобразование Фурье
    и фазовую коррекцию комплексных сигналов
    FM-радара для получения карты дальности и скорости целей

    Args:
        globals (dict[str, Any]): Глобальные переменные

    Returns:
        _Array[tuple[int, int, int], complexfloating[_32Bit, _32Bit]]
    """

    c = globals["c"]
    Wd = globals["Wd"]
    H = globals["H"] if globals["H"] > 0 else 10.0
    ChannelN = globals["ChannelN"]
    Nimp = globals["Nimp"]
    SigCN = globals["SigCN"]
    SigSN = globals["SigSN"]
    Rs = globals.get("Rs", {"Rmin": 0.0, "Rmax": 5.1, "Log": False, "GB": 20})
    test = globals.get("test", {"canceling": False, "h": {}, "fstep": [100, 100]})

    SigN = SigCN + 1j * SigSN

    # Расчет параметров обработки
    dR = 0.5 * c / Wd
    RCmax = round((Rs["Rmax"] - Rs["Rmin"]) * H / dR)

    # Инициализация матрицы результатов
    RLI = np.zeros((ChannelN, RCmax, Nimp), dtype=np.complex64)

    # Обработка по каналам
    for ChCnt in range(ChannelN):
        if test["canceling"]:
            break
        Sig1 = SigN[ChCnt, :, :]
        Sig2 = np.fft.fft(Sig1, axis=1)
        Sig3 = np.fft.fft(Sig2, axis=0)
        RLI[ChCnt, :, :] = np.abs(Sig3.T)[:RCmax, :Nimp]

    # Коррекция фазы и сохранение полных данных
    RLIFM = np.zeros_like(RLI)
    for ChCnt in range(ChannelN):
        RLI1 = RLI[ChCnt, :, :]
        RLIFM[ChCnt, :, :] = np.roll(np.fliplr(RLI1), shift=Nimp // 2, axis=1)

    # Сохраняем результаты обратно в globals
    globals["RLI"] = RLI
    globals["RLIFM"] = RLIFM
    return globals


def plot_fm_radar_results(globals: dict):
    """
    Отображение результатов FM-радара

    Строит графики изображений по данным
    обработки FM-радара из globals.

    Args:
        globals (dict[str, Any]): Глобальные переменные
    """

    # Проверка наличия результатов
    if "RLI" not in globals or globals["RLI"] is None:
        raise ValueError("Сначала выполните process_fm_radar()")

    RLI = globals["RLI"]
    c = globals["c"]
    Wd = globals["Wd"]
    H = globals["H"]
    Nimp = globals["Nimp"]
    Timp = globals["Timp"]
    Rs = globals.get("Rs", {"Rmin": 0.0, "Rmax": 5.1, "Log": False, "GB": 20})
    ChannelN = globals["ChannelN"]

    dR = 0.5 * c / Wd
    Dal = dR * np.arange(RLI.shape[1]) + Rs["Rmin"] * H
    Dop = (0.5 - Nimp / 2 + np.arange(Nimp)) / (Timp * Nimp)

    fig = plt.figure(figsize=(15, 5))
    fig.canvas.manager.set_window_title("Дальность-доплер")

    ChCntMax = min(3, ChannelN)
    ch_indices = np.linspace(0, ChannelN - 1, ChCntMax, dtype=int)

    for i, ChCnt in enumerate(ch_indices):
        RLI1f = RLI[ChCnt, :, :]
        plt.subplot(1, ChCntMax, i + 1)
        if Rs["Log"]:
            plt.contour(Dop * 1e-3, Dal, np.log(RLI1f), Rs["GB"])
        else:
            plt.contour(Dop * 1e-3, Dal, RLI1f, Rs["GB"])
        plt.grid(True)
        plt.xlabel("Доплер (кГц)", fontsize=9)
        plt.ylabel("Дальность координат (м)", fontsize=9)
        plt.title(f"Канал {ChCnt + 1}", fontsize=9, fontweight="normal")

    if ChannelN == 1:
        plt.title("РЛ изображение", fontsize=9, fontweight="normal")

    plt.tight_layout()
    plt.show()


def save_fm_radar_results(globals: dict, filename: str = "RLIfm.npz"):
    """
    Сохранение результатов FM-радара

    Сохраняет обработанные данные FM-радара
    и параметры в файл формата .npz.

    Args:
        globals (dict[str, Any]): Глобальные переменные
        filename (str, optional): Имя файла. Defaults to "RLIfm.npz".
    """

    if "RLIFM" not in globals or globals["RLIFM"] is None:
        raise ValueError("Сначала выполните process_fm_radar()")
    np.savez(filename, RLIFM=globals["RLIFM"], Rs=globals.get("Rs", {}))
