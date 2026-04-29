import matplotlib.pyplot as plt
import numpy as np

from helpers import copy_fig_to_clipboard
from state import state


def do_step():
    """
    Расчёт относительных мощностей излучателей МИ.
    На входе значения для КЦО от -50 до +50, например Mi.z=21; Mi.y=-18;
    а также Mi.dx=? по умолчанию 1м, Mi.dz=? по умолчанию 1м,
    а также, если все Изл.МИ включены, то Mi.a = [1, 1, 1, 1]
    n=0:3 — считаем сразу для 4-х изл.МИ
    """
    try:
        # Обновляем время
        # state.t = state.t + state.Step * 0.001
        state.t = 0 + state.Step * 0.001

        Mi = state.Mi

        # Координаты излучателей МИ
        Mi.Z = np.array([50, -50, 0, 0], dtype=float)
        Mi.Y = np.array([0, 0, 50, -50], dtype=float)

        # Приводим скалярные поля к float на случай если пришли строкой от клиента
        Mi.z = float(Mi.z)
        Mi.y = float(Mi.y)
        Mi.a = np.array(Mi.a, dtype=float)

        # tmpa — проекция разности на биссектрису
        tmpa = np.abs(Mi.Z + Mi.Y - Mi.z - Mi.y) / np.sqrt(2)

        # tmpd — евклидово расстояние от КЦО до каждого излучателя
        tmpd = np.sqrt((Mi.Z - Mi.z) ** 2 + (Mi.Y - Mi.y) ** 2)

        # Расчёт относительных мощностей
        Mi.Pi = Mi.a * tmpa * np.sqrt(np.maximum(tmpd**2 - tmpa**2, 0)) / 50

    except Exception:
        # Доопределяем параметры на случай 1-го запуска до определения всех параметров
        state.Mi.z = 0
        state.Mi.y = 0
        state.Mi.a = np.array([1, 1, 1, 1], dtype=float)
        state.Mi.Pi = np.array([1, 1, 1, 1], dtype=float)

    # ==== Построение графика мощностей излучателей ====
    Mi = state.Mi
    labels = ["МИ-1\n(Z=+50)", "МИ-2\n(Z=-50)", "МИ-3\n(Y=+50)", "МИ-4\n(Y=-50)"]
    colors = ["steelblue", "tomato", "mediumseagreen", "darkorange"]

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # --- График 1: столбчатая диаграмма мощностей ---
    ax1 = axes[0]
    bars = ax1.bar(labels, Mi.Pi, color=colors, edgecolor="black", alpha=0.85)
    ax1.set_title("Относительные мощности излучателей МИ")
    ax1.set_ylabel("Мощность (норм.)")
    ax1.set_ylim(bottom=0)
    ax1.grid(axis="y", linestyle="--", alpha=0.6)
    # Подписи значений над столбцами
    for bar, val in zip(bars, Mi.Pi):
        ax1.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.01,
            f"{float(val):.3f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    # --- График 2: положение КЦО и излучателей на плоскости Z-Y ---
    ax2 = axes[1]
    # Нормируем мощности для размера маркеров (минимум 50 для видимости)
    marker_sizes = np.maximum(Mi.Pi / (np.max(Mi.Pi) + 1e-9) * 400, 50)
    ax2.scatter(
        Mi.Z,
        Mi.Y,
        s=marker_sizes,
        c=colors,
        edgecolors="black",
        alpha=0.85,
        zorder=3,
        label="Излучатели МИ",
    )
    ax2.scatter(
        Mi.z,
        Mi.y,
        s=120,
        c="black",
        marker="x",
        linewidths=2,
        zorder=4,
        label=f"КЦО ({Mi.z}, {Mi.y})",
    )
    # Линии от КЦО до каждого излучателя
    for i in range(len(Mi.Z)):
        ax2.plot(
            [Mi.z, Mi.Z[i]],
            [Mi.y, Mi.Y[i]],
            color=colors[i],
            linestyle="--",
            alpha=0.5,
            linewidth=1,
        )
    ax2.set_xlim(-70, 70)
    ax2.set_ylim(-70, 70)
    ax2.set_xlabel("Z [м]")
    ax2.set_ylabel("Y [м]")
    ax2.set_title("Расположение излучателей и КЦО")
    ax2.axhline(0, color="gray", linewidth=0.5)
    ax2.axvline(0, color="gray", linewidth=0.5)
    ax2.grid(True, linestyle="--", alpha=0.4)
    ax2.legend()

    plt.suptitle(f"МИ | t = {state.t:.3f} с", fontsize=12)
    plt.tight_layout()
    copy_fig_to_clipboard()  # Сохранение графика в буфер обмена
