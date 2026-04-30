import matplotlib.pyplot as plt
import numpy as np

from helpers import copy_fig_to_clipboard
from state import state


def do_step():
    """
    Расчёт относительных мощностей излучателей МИ.
    Аналог Do_Step.m (первый шаг ПНМ).
    На входе: Mi.z, Mi.y — координаты КЦО от -50 до +50;
              Mi.a       — маски включения излучателей [1,1,1,1].
    """
    try:
        state.t = int(state.t + state.Step * 0.001)

        Mi = state.Mi
        Mi.Z = np.array([50.0, -50.0, 0.0, 0.0])
        Mi.Y = np.array([0.0, 0.0, 50.0, -50.0])

        Mi.z = float(Mi.z)
        Mi.y = float(Mi.y)
        Mi.a = np.array(Mi.a, dtype=float)

        tmpa = np.abs(Mi.Z + Mi.Y - Mi.z - Mi.y) / np.sqrt(2)
        tmpd = np.sqrt((Mi.Z - Mi.z) ** 2 + (Mi.Y - Mi.y) ** 2)
        Mi.Pi = Mi.a * tmpa * np.sqrt(np.maximum(tmpd**2 - tmpa**2, 0)) / 50

    except Exception:
        state.Mi.z = 0
        state.Mi.y = 0
        state.Mi.a = np.array([1.0, 1.0, 1.0, 1.0])
        state.Mi.Pi = np.array([1.0, 1.0, 1.0, 1.0])

    Mi = state.Mi
    labels = ["МИ-1\n(Z=+50)", "МИ-2\n(Z=-50)", "МИ-3\n(Y=+50)", "МИ-4\n(Y=-50)"]
    colors = ["steelblue", "tomato", "mediumseagreen", "darkorange"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    bars = ax1.bar(labels, Mi.Pi, color=colors, edgecolor="black", alpha=0.85)
    ax1.set_title(
        "Относительные мощности излучателей МИ", fontsize=9, fontweight="normal"
    )
    ax1.set_ylabel("Мощность (норм.)", fontsize=9)
    ax1.set_ylim(bottom=0)
    ax1.grid(axis="y", linestyle="--", alpha=0.6)
    for bar, val in zip(bars, Mi.Pi):
        ax1.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.01,
            f"{float(val):.3f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    marker_sizes = np.maximum(Mi.Pi / (np.max(Mi.Pi) + 1e-9) * 400, 50)
    ax2.scatter(
        Mi.Z, Mi.Y, s=marker_sizes, c=colors, edgecolors="black", alpha=0.85, zorder=3
    )
    ax2.scatter(
        Mi.z,
        Mi.y,
        s=120,
        c="black",
        marker="x",
        linewidths=2,
        zorder=4,
        label=f"КЦО ({Mi.z:.0f}, {Mi.y:.0f})",
    )
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
    ax2.set_xlabel("Z [м]", fontsize=9)
    ax2.set_ylabel("Y [м]", fontsize=9)
    ax2.set_title("Расположение излучателей и КЦО", fontsize=9, fontweight="normal")
    ax2.axhline(0, color="gray", linewidth=0.5)
    ax2.axvline(0, color="gray", linewidth=0.5)
    ax2.grid(True, linestyle="--", alpha=0.4)
    ax2.legend(fontsize=9)

    plt.suptitle(f"МИ | t = {state.t:.3f} с", fontsize=10)
    plt.tight_layout()
    copy_fig_to_clipboard()
