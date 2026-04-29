import matplotlib.pyplot as plt
import numpy as np

from helpers import save_fig_as_bmp


def show_relief(Relief):
    """
    Построение поверхности и сохранение в формате BMP в корень проекта
    """
    test = {"h": [None, None, None], "fstep": [100, 100]}
    Sf = {
        "x_size": Relief.shape[1],
        "z_size": Relief.shape[0],
        "med_shift": min(Relief.shape) / 2 - 0.5,
        "XZstep": 10,
        "Relief": "Example Relief",
    }

    if test["h"][2] is None:
        test["h"][2] = plt.figure()

    plt.get_current_fig_manager().set_window_title("Вид поверхности")

    try:
        tmp = (
            plt.get_current_fig_manager().window.winfo_width(),
            plt.get_current_fig_manager().window.winfo_height(),
        )
    except AttributeError:
        tmp = (800, 600)

    x_pos = (test["h"][2].number - 1) * test["fstep"][0]
    y_pos = (test["h"][2].number - 1) * test["fstep"][1]

    width = tmp[0] if tmp[0] > 0 else 800
    height = tmp[1] if tmp[1] > 0 else 600

    try:
        plt.get_current_fig_manager().window.geometry(
            f"{width}x{height}+{x_pos}+{y_pos}"
        )
    except Exception:
        pass

    mm = (np.min(Relief), np.max(Relief))

    plt.clf()
    X, Z = np.meshgrid(
        (np.arange(1, Sf["x_size"] + 1) - Sf["med_shift"]),
        (np.arange(1, Sf["z_size"] + 1) - Sf["med_shift"]),
    )

    plt.contourf(X * Sf["XZstep"], Z * Sf["XZstep"], Relief)
    plt.axis("equal")
    plt.gca().invert_yaxis()
    plt.axis("tight")

    plt.xlabel("x (м)", fontsize=9)
    plt.ylabel("z (м)", fontsize=9)
    plt.title(
        f'Вид рельефа "{Sf["Relief"]}"; высоты от {int(mm[0])} до {int(mm[1])} м',
        fontsize=9,
        fontweight="normal",
    )
    plt.colorbar()

    save_fig_as_bmp("relief.bmp")
