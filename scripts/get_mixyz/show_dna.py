import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

from helpers.save_bmp import save_fig_as_bmp
from state import state

from .set_mi_param import set_mi_param
from .set_rv_param import set_rv_param


def _fun_dir_pat(
    angle: np.ndarray,
    half_width: complex,
    side: int,
    mode: str,
) -> np.ndarray:
    """
    Аппроксимация ДНА (диаграммы направленности антенны).

    angle      — угловое отклонение от оси, рад.
                 Комплексный вход задаёт 2D-паттерн: real=X, imag=Z.
    half_width — полуширина ДНА, рад.
                 Комплексный вход: real=ширина по X, imag=ширина по Z.
    side       — 0: полная ДНА; >0: только правая полуось; <0: только левая.
    mode       — аппроксимация: 'SC...' — sinc², 'G' — Гауссова, иначе — cos².
    """
    angle = np.atleast_1d(np.asarray(angle, dtype=complex))
    hw = complex(half_width)
    hw_x = float(np.real(hw)) or 1.0
    hw_z = float(np.imag(hw)) or hw_x  # если не задана — как по X

    def _1d(a: np.ndarray, hw: float) -> np.ndarray:
        if hw == 0:
            return np.ones_like(a, dtype=float)
        x = a / hw
        if mode == "G":
            return np.exp(-(x**2) * np.log(2))  # -3 дБ на half_width
        elif mode.startswith("SC"):
            pi_x = np.pi * x
            sinc = np.where(np.abs(pi_x) < 1e-9, 1.0, np.sin(pi_x) / pi_x)
            return sinc**2
        else:
            return np.cos(np.clip(a, -np.pi / 2, np.pi / 2)) ** 2

    angle_x = np.real(angle)
    angle_z = np.imag(angle)

    result = _1d(angle_x, hw_x)
    if np.any(angle_z != 0) or np.imag(hw) != 0:
        result = result * _1d(angle_z, hw_z)

    result = np.abs(result).astype(float)

    if side > 0:
        result[angle_x < 0] = 0.0
    elif side < 0:
        result[angle_x > 0] = 0.0

    return result


def show_dna():
    """
    Отображение ДНА по параметрам из state.

    Для одноканальной системы (ChannelN==1) строит сечения ДНА передающей
    и приёмной антенн в плоскостях XY и ZY.
    Для двухканальной (ChannelN==2) добавляет второй канал приёмной антенны.
    Для ChannelN>2 строит сечения всех каналов (не более 9).
    Если DNA2 задана комплексным числом (real=ширина_X, imag=ширина_Z),
    дополнительно строится 3D-форма ДНА первой приёмной антенны.
    """
    set_rv_param()  # Установка общих параметров РВС/РЛС
    set_mi_param()  # Установка параметров-настройки МИ

    ag = np.arange(-70, 71, dtype=float)  # диапазон углов построения ДНА

    # --- параметры из state ---
    # DNA1n/DNA2n — ширина ДНА в градусах (DNA2 может быть комплексным:
    # real=ширина по X, imag=ширина по Z для неосесимметричной ДНА)
    n_ch = max(state.ChannelN, 1)
    vidDNA = state.vidDNA

    # Текущий state хранит единственный набор параметров — реплицируем по каналам
    DNA1_arr = [float(state.DNA1[0])] * n_ch
    DNA2_arr = [float(state.DNA2[0])] * n_ch
    AnglX_Prm = [float(state.AnglX_Prm[0])] * n_ch
    AnglZ_Prm = [float(state.AnglZ_Prm[0])] * n_ch
    AnglX_Prd = [float(state.AnglX_Prd[0])] * n_ch
    AnglZ_Prd = [float(state.AnglZ_Prd[0])] * n_ch

    # --- выбор компоновки фигуры ---
    # 3D-подграфик строится только при неосесимметричной ДНА (imag(DNA2) > 0)
    has_3d = max(np.imag(d) for d in DNA2_arr) > 0

    if has_3d:
        fig = plt.figure(figsize=(10, 10))
        ax3d = fig.add_subplot(2, 1, 1, projection="3d")
        ax2d = fig.add_subplot(2, 1, 2)
    else:
        fig, ax2d = plt.subplots(1, 1, figsize=(6, 3))
        ax3d = None

    try:
        fig.canvas.manager.set_window_title("Параметры локатора")
    except Exception:
        pass

    # --- 3D-форма ДНА (только для неосесимметричной) ---
    if has_3d and ax3d is not None:
        X, Y = np.meshgrid(ag, ag)
        angle_2d = np.deg2rad(X - AnglX_Prm[0]) + 1j * np.deg2rad(Y - AnglZ_Prm[0])
        hw_2d = np.deg2rad(np.real(DNA2_arr[0])) + 1j * np.deg2rad(np.imag(DNA2_arr[0]))
        Z = _fun_dir_pat(angle_2d.ravel(), hw_2d, 0, vidDNA).reshape(X.shape)

        ax3d.plot_surface(X, Y, Z, cmap="viridis", alpha=0.85)
        ax3d.set_title(
            f"Форма ДН 1-й приемной антенны, аппроксимация {vidDNA}",
            fontsize=9,
            fontweight="normal",
        )
        ax3d.legend(
            [
                f"DNA2={int(np.real(DNA2_arr[0]))}x{int(np.imag(DNA2_arr[0]))},"
                f"\nAnglX={int(AnglX_Prm[0])},\nAnglZ={int(AnglZ_Prm[0])}"
            ],
            fontsize=9,
        )
        ax3d.invert_yaxis()
        ax3d.set_xlim(ag[0], ag[-1])
        ax3d.set_ylim(ag[0], ag[-1])
        ax3d.grid(True)
        ax3d.set_xlabel("Угол θ_XZ (градусы)", fontsize=9)
        ax3d.set_ylabel("Угол θ_Y (градусы)", fontsize=9)

    # --- 2D сечения ДНА ---
    n_ch_state = state.ChannelN

    if n_ch_state <= 1:
        curves = np.vstack(
            [
                1.0
                * _fun_dir_pat(
                    np.deg2rad(ag - AnglX_Prd[0]),
                    np.deg2rad(DNA1_arr[0] / 2),
                    0,
                    vidDNA,
                ),
                0.9
                * _fun_dir_pat(
                    np.deg2rad(ag - AnglX_Prm[0]),
                    np.deg2rad(np.real(DNA2_arr[0]) / 2),
                    0,
                    vidDNA,
                ),
                0.8
                * _fun_dir_pat(
                    np.deg2rad(ag - AnglZ_Prd[0]),
                    np.deg2rad(DNA1_arr[0] / 2),
                    0,
                    vidDNA,
                ),
                0.7
                * _fun_dir_pat(
                    np.deg2rad(ag - AnglZ_Prm[0]),
                    np.deg2rad(np.real(DNA2_arr[0]) / 2),
                    0,
                    vidDNA,
                ),
            ]
        )
        ax2d.plot(ag, curves.T)
        ax2d.legend(
            [
                f"DNA1={int(DNA1_arr[0])}, AnglX={int(AnglX_Prd[0])}",
                f"DNA2={int(np.real(DNA2_arr[0]))}, AnglX={int(AnglX_Prm[0])}",
                f"DNA1={int(DNA1_arr[0])}, AnglZ={int(AnglZ_Prd[0])}",
                f"DNA2={int(np.real(DNA2_arr[0]))}, AnglZ={int(AnglZ_Prm[0])}",
            ],
            loc="upper left",
            fontsize=9,
        )
        ax2d.set_title(
            f"Сечения ДН перед. и приемной антенн в плоскостях XY,ZY, аппроксимация {vidDNA}",
            fontsize=9,
            fontweight="normal",
        )

    elif n_ch_state == 2:
        curves = np.vstack(
            [
                1.0
                * _fun_dir_pat(
                    np.deg2rad(ag - AnglX_Prd[0]),
                    np.deg2rad(DNA1_arr[0] / 2),
                    0,
                    vidDNA,
                ),
                0.9
                * _fun_dir_pat(
                    np.deg2rad(ag - AnglX_Prm[0]),
                    np.deg2rad(np.real(DNA2_arr[0]) / 2),
                    0,
                    vidDNA,
                ),
                0.8
                * _fun_dir_pat(
                    np.deg2rad(ag - AnglZ_Prd[0]),
                    np.deg2rad(DNA1_arr[0] / 2),
                    0,
                    vidDNA,
                ),
                0.7
                * _fun_dir_pat(
                    np.deg2rad(ag - AnglZ_Prm[0]),
                    np.deg2rad(np.real(DNA2_arr[0]) / 2),
                    0,
                    vidDNA,
                ),
                0.6
                * _fun_dir_pat(
                    np.deg2rad(ag - AnglX_Prm[1]),
                    np.deg2rad(np.real(DNA2_arr[1]) / 2),
                    0,
                    vidDNA,
                ),
                0.5
                * _fun_dir_pat(
                    np.deg2rad(ag - AnglZ_Prm[1]),
                    np.deg2rad(np.real(DNA2_arr[1]) / 2),
                    0,
                    vidDNA,
                ),
            ]
        )
        ax2d.plot(ag, curves.T)
        ax2d.legend(
            [
                f"DNA1.1={int(DNA1_arr[0])}, AnglX={int(AnglX_Prd[0])}",
                f"DNA2.1={int(np.real(DNA2_arr[0]))}, AnglX={int(AnglX_Prm[0])}",
                f"DNA1.1={int(DNA1_arr[0])}, AnglZ={int(AnglZ_Prd[0])}",
                f"DNA2.1={int(np.real(DNA2_arr[0]))}, AnglZ={int(AnglZ_Prm[0])}",
                f"DNA2.2={int(np.real(DNA2_arr[1]))}, AnglX={int(AnglX_Prm[1])}",
                f"DNA2.2={int(np.real(DNA2_arr[1]))}, AnglZ={int(AnglZ_Prm[1])}",
            ],
            loc="upper left",
            fontsize=9,
        )
        ax2d.set_title(
            f"Сечения ДН 1 передающей и 1-2 приемной антенн в плоск. XY,ZY, аппроксимация {vidDNA}",
            fontsize=9,
            fontweight="normal",
        )

    else:  # ChannelN > 2
        ch_max = min(9, n_ch_state)
        ch_indices = np.round(np.linspace(0, n_ch_state - 1, ch_max)).astype(int)
        for ch in ch_indices:
            scale = ch + 1  # MATLAB: ChCnt идёт с 1
            curves = np.vstack(
                [
                    (0.8 + scale / 5)
                    * _fun_dir_pat(
                        np.deg2rad(ag - AnglX_Prm[ch]),
                        np.deg2rad(np.real(DNA2_arr[ch]) / 2),
                        0,
                        vidDNA,
                    ),
                    (0.9 + scale / 5)
                    * _fun_dir_pat(
                        np.deg2rad(ag - AnglZ_Prm[ch]),
                        np.deg2rad(np.real(DNA2_arr[ch]) / 2),
                        0,
                        vidDNA,
                    ),
                ]
            )
            ax2d.plot(ag, curves.T)
        ax2d.legend(
            [
                f"DNA2.1={int(np.real(DNA2_arr[0]))}, AnglX={int(AnglX_Prm[0])}",
                f"DNA2.1={int(np.real(DNA2_arr[0]))}, AnglZ={int(AnglZ_Prm[0])}",
            ],
            loc="upper left",
            fontsize=9,
        )
        ax2d.set_title(
            f"Сечения ДН всех приемных антенн в плоскостях XY,ZY, аппроксимация {vidDNA}",
            fontsize=9,
            fontweight="normal",
        )

    ax2d.grid(True)
    ax2d.autoscale(axis="both", tight=True)
    ax2d.set_xlabel("Угол θ_XY, θ_ZY (градусы)", fontsize=9)
    ax2d.set_ylabel("Коэфф. (нормир. к номеру ДНА)", fontsize=8)

    plt.tight_layout()
    save_fig_as_bmp("resultFig1.bmp")
