import math

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 (подключение 3D проекции)

from helpers import save_fig_as_bmp
from state import state

from .set_mi_param import set_mi_param
from .set_rv_param import set_rv_param


def get_mixyz():
    """
    Расчёт геометрии антенных элементов МИ и построение 3D-графика.
    Результаты записываются напрямую в state.state.Mi.
    График копируется в буфер обмена (Windows).
    """

    set_rv_param()  # Установка общих параметров РВС/РЛС
    set_mi_param()  # Установка параметров-настройки МИ (расчёт мощностей)

    # центральные позиции
    state.Mi.sx = [
        0,
        1,
        1,
        2,
        -1,
        0,
        -1,
        0,
        -2,
        2,
        3,
        1,
        -2,
        -1,
        -3,
        0,
        2,
        3,
        1,
        4,
        -2,
        -1,
        -3,
        0,
        -4,
        3,
        4,
        2,
        5,
        1,
        -3,
        -2,
        -4,
        -1,
        -5,
        0,
        3,
        4,
        2,
        5,
        1,
        6,
        -3,
        -2,
        -4,
        -1,
        -5,
        0,
        -6,
        4,
        5,
        3,
        6,
        2,
        7,
        1,
        0,
        -4,
        -3,
        -5,
        -2,
        -6,
        -1,
        -7,
        4,
        5,
        3,
        6,
        2,
        7,
        1,
        8,
        -4,
        -3,
        -5,
        -2,
        -6,
        -1,
        -7,
        -8,
        0,
        5,
        6,
        4,
        7,
        3,
        8,
        2,
        1,
        -5,
        -4,
        -6,
        -3,
        -7,
        -2,
        -8,
        -1,
        0,
        -9,
        5,
        6,
        4,
        7,
        3,
        8,
        2,
        9,
        -1,
        -10,
        -5,
        -4,
        -6,
        -3,
        -7,
        -2,
        -8,
        -9,
        1,
        9,
        10,
        0,
    ]
    state.Mi.sz = [
        0,
        1,
        -1,
        0,
        1,
        2,
        -1,
        -2,
        0,
        2,
        1,
        3,
        2,
        3,
        1,
        4,
        -2,
        -1,
        -3,
        0,
        -2,
        -3,
        -1,
        -4,
        0,
        3,
        2,
        4,
        1,
        5,
        3,
        4,
        2,
        5,
        1,
        6,
        -3,
        -2,
        -4,
        -1,
        -5,
        0,
        -3,
        -4,
        -2,
        -5,
        -1,
        -6,
        0,
        4,
        3,
        5,
        2,
        6,
        1,
        7,
        8,
        4,
        5,
        3,
        6,
        2,
        7,
        1,
        -4,
        -3,
        -5,
        -2,
        -6,
        -1,
        -7,
        0,
        -4,
        -5,
        -3,
        -6,
        -2,
        -7,
        -1,
        0,
        -8,
        5,
        4,
        6,
        3,
        7,
        2,
        8,
        9,
        5,
        6,
        4,
        7,
        3,
        8,
        2,
        9,
        10,
        1,
        -5,
        -4,
        -6,
        -3,
        -7,
        -2,
        -8,
        1,
        -9,
        0,
        -5,
        -6,
        -4,
        -7,
        -3,
        -8,
        -2,
        -1,
        -9,
        -1,
        0,
        -10,
    ]

    # Если Nmax не задан — вычисляем из размера sx
    if state.Mi.Nmax == 0:
        state.Mi.Nmax = len(state.Mi.sx) * 4

    # Количество групп по 4 элемента (не выходим за пределы sx/sz)
    sn = min((state.Mi.Nmax + 3) // 4, len(state.Mi.sx))

    state.Mi.Ants = 0  # счётчик — кол-во антенных элементов МИ

    # Подготовим чистые массивы координат антенн МИ
    state.Mi.Mx = np.zeros(state.Mi.Nmax, dtype=float)
    state.Mi.Mz = np.zeros(state.Mi.Nmax, dtype=float)
    state.Mi.Ax = np.zeros(state.Mi.Nmax, dtype=float)
    state.Mi.Az = np.zeros(state.Mi.Nmax, dtype=float)
    state.Mi.Rt = np.zeros(state.Mi.Nmax, dtype=float)
    state.Mi.My = np.zeros(state.Mi.Nmax, dtype=float)

    # Угловые апертуры по осям
    state.AlfaX = math.atan(state.Mi.Rz / 2.0 / state.Mi.Rs)
    state.AlfaZ = math.atan(state.Mi.Ry / 2.0 / state.Mi.Rs)

    # TODO поменять логику отрисовку этого графика
    # Настройка рисунка
    fig = plt.figure(figsize=(6, 6), dpi=100)
    ax = fig.add_subplot(111, projection="3d")
    ax.scatter(
        [0], [0], [0], marker="h", color="magenta"
    )  # позиция центральной точки АС РЛС

    for k in range(sn):
        base = k * 4

        # Проверка границ (нужны хотя бы два слота для первой пары)
        if base + 1 >= state.Mi.Nmax:
            break

        # --- 2 горизонтальных элемента ---
        state.Mi.Ax[base + 0] = state.AlfaX * (state.Mi.sx[k] + 0.5)
        state.Mi.Mx[base + 0] = math.tan(state.Mi.Ax[base + 0]) * state.Mi.Rs * 2.0
        state.Mi.Az[base + 0] = state.AlfaZ * state.Mi.sz[k]
        state.Mi.Mz[base + 0] = math.tan(state.Mi.Az[base + 0]) * state.Mi.Rs * 2.0

        state.Mi.Ax[base + 1] = state.AlfaX * (state.Mi.sx[k] - 0.5)
        state.Mi.Mx[base + 1] = math.tan(state.Mi.Ax[base + 1]) * state.Mi.Rs * 2.0
        state.Mi.Az[base + 1] = state.AlfaZ * state.Mi.sz[k]
        state.Mi.Mz[base + 1] = math.tan(state.Mi.Az[base + 1]) * state.Mi.Rs * 2.0

        # Проверка выхода за границы апертуры
        if (
            abs(state.Mi.Mx[base + 0]) > state.Mi.Zmax
            or abs(state.Mi.Mx[base + 1]) > state.Mi.Zmax
            or abs(state.Mi.Mz[base + 0]) > state.Mi.Ymax
            or abs(state.Mi.Mz[base + 1]) > state.Mi.Ymax
        ):
            state.Mi.Mx[base + 0] = state.Mi.Mz[base + 0] = 0.0
            state.Mi.Mx[base + 1] = state.Mi.Mz[base + 1] = 0.0

            continue

        state.Mi.Rt[base + 0] = math.sqrt(
            state.Mi.Mx[base + 0] ** 2 + state.Mi.Rs**2 + state.Mi.Mz[base + 0] ** 2
        )
        state.Mi.Rt[base + 1] = math.sqrt(
            state.Mi.Mx[base + 1] ** 2 + state.Mi.Rs**2 + state.Mi.Mz[base + 1] ** 2
        )
        state.Mi.Ants += 2  # счётчик — кол-во антенных элементов МИ

        # --- 2 вертикальных элемента (если есть место) ---
        if base + 3 < state.Mi.Nmax:
            state.Mi.Ax[base + 2] = state.AlfaX * state.Mi.sx[k]
            state.Mi.Mx[base + 2] = math.tan(state.Mi.Ax[base + 2]) * state.Mi.Rs * 2.0
            state.Mi.Az[base + 2] = state.AlfaZ * (state.Mi.sz[k] + 0.5)
            state.Mi.Mz[base + 2] = math.tan(state.Mi.Az[base + 2]) * state.Mi.Rs * 2.0

            state.Mi.Ax[base + 3] = state.AlfaX * state.Mi.sx[k]
            state.Mi.Mx[base + 3] = math.tan(state.Mi.Ax[base + 3]) * state.Mi.Rs * 2.0
            state.Mi.Az[base + 3] = state.AlfaZ * (state.Mi.sz[k] - 0.5)
            state.Mi.Mz[base + 3] = math.tan(state.Mi.Az[base + 3]) * state.Mi.Rs * 2.0

            # Проверка выхода за границы апертуры (зануляем все 4 слота как в оригинале)
            if (
                abs(state.Mi.Mx[base + 2]) > state.Mi.Zmax
                or abs(state.Mi.Mx[base + 3]) > state.Mi.Zmax
                or abs(state.Mi.Mz[base + 2]) > state.Mi.Ymax
                or abs(state.Mi.Mz[base + 3]) > state.Mi.Ymax
            ):
                state.Mi.Mx[base + 0] = state.Mi.Mz[base + 0] = 0.0
                state.Mi.Mx[base + 1] = state.Mi.Mz[base + 1] = 0.0
                state.Mi.Mx[base + 2] = state.Mi.Mz[base + 2] = 0.0
                state.Mi.Mx[base + 3] = state.Mi.Mz[base + 3] = 0.0
                continue

            state.Mi.Rt[base + 2] = math.sqrt(
                state.Mi.Mx[base + 2] ** 2 + state.Mi.Rs**2 + state.Mi.Mz[base + 2] ** 2
            )
            state.Mi.Rt[base + 3] = math.sqrt(
                state.Mi.Mx[base + 3] ** 2 + state.Mi.Rs**2 + state.Mi.Mz[base + 3] ** 2
            )
            state.Mi.Ants += 2  # счётчик — кол-во антенных элементов МИ

        print("TUTU", state.test.figext)
        # --- Отрисовка согласно test.figext ---
        if state.test.figext > 0:
            # Позиции 2-х горизонтальных ЭлАс МИ
            ax.plot(
                [state.Mi.Mx[base + 0], state.Mi.Mx[base + 1]],
                [state.Mi.Rs, state.Mi.Rs],
                [state.Mi.Mz[base + 0], state.Mi.Mz[base + 1]],
                "-ro",
            )
            # Позиции 2-х вертикальных ЭлАс МИ
            if base + 3 < state.Mi.Nmax:
                ax.plot(
                    [state.Mi.Mx[base + 2], state.Mi.Mx[base + 3]],
                    [state.Mi.Rs, state.Mi.Rs],
                    [state.Mi.Mz[base + 2], state.Mi.Mz[base + 3]],
                    "-bo",
                )

        if state.test.figext >= 0:
            # Центральная точка группы из 4-х ЭлАс МИ
            ax.scatter(
                [state.Mi.sx[k] * state.Mi.Rz],
                [state.Mi.Rs],
                [state.Mi.sz[k] * state.Mi.Ry],
                marker="D",
                color="k",
            )

    # --- Финальные расчёты ---
    state.Mi.Dists = np.sqrt(
        state.Mi.Mx**2 + state.Mi.Rs**2 + state.Mi.Mz**2
    )  # расстояния до центра АС РЛС

    mask = state.Mi.Dists > state.Mi.Rs
    min_dist = np.min(state.Mi.Dists[mask]) if np.any(mask) else state.Mi.Rs
    state.Mi.Diffs = (
        state.Mi.Dists - min_dist
    )  # для расчёта длины выравнивающих кабелей

    active_diffs = state.Mi.Diffs[state.Mi.Diffs >= 0]
    state.Mi.dDist = (
        float(np.max(active_diffs)) if len(active_diffs) > 0 else 0.0
    )  # максимальная разница расстояний

    if state.Mi.Nmax < len(state.Mi.Mx):
        state.Mi.Nmax = len(state.Mi.Mx)

    state.Mi.My[:] = state.Mi.Rs  # все в одной плоскости

    # --- Оформление графика ---
    ax.set_title(
        f"Геометрия МИ для state.Mi.Ants={state.Mi.Ants}",
        fontsize=9,
        fontweight="normal",
    )
    ax.set_xlabel("z (м)", fontsize=9)
    ax.set_ylabel("x (м)", fontsize=9)
    ax.set_zlabel("y (м)", fontsize=9)
    ax.grid(True)
    try:
        ax.set_box_aspect([1, 1, 1])
    except Exception:
        pass

    print(
        f"Angles of first elements have AlfaX={state.AlfaX / math.pi * 180 * 2:.6g}, AlfaZ={state.AlfaZ / math.pi * 180 * 2:.6g}"
    )

    plt.tight_layout()
    save_fig_as_bmp("resultFig1.bmp")
