import numpy as np


def get_forest(
    n_trees=50,
    area_size=(200, 200),
    h_mean=20,
    h_std=5,
    r_mean=5,
    r_std=2,
    base_height=0,
):
    """
    Генерация леса (Type=4).
    """
    x = (np.random.rand(n_trees) - 0.5) * area_size[0]
    z = (np.random.rand(n_trees) - 0.5) * area_size[1]
    h = np.abs(np.random.normal(h_mean, h_std, n_trees))
    r = np.abs(np.random.normal(r_mean, r_std, n_trees))

    y_base = np.full(n_trees, base_height)
    y_top = base_height + h

    return {
        "x": x,
        "z": z,
        "y_base": y_base,
        "y_top": y_top,
        "h": h,
        "r": r,
    }


def plot_forest(forest, ax):
    """
    Визуализация леса (стволы + вершины).
    """
    for i in range(len(forest["x"])):
        # Ствол
        # ax.plot(
        #     [forest["x"][i], forest["x"][i]],
        #     [forest["z"][i], forest["z"][i]],
        #     [forest["y_base"][i], forest["y_top"][i]],
        #     c="saddlebrown",
        #     linewidth=2,
        # )

        # Крона (верхушка)
        ax.scatter(
            forest["x"][i],
            forest["z"][i],
            forest["y_top"][i],
            c="green",
            s=forest["r"][i] * 20,
            alpha=0.6,
        )
