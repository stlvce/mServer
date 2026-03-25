import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from PIL import Image
import io


from state import state

from .get_forest import get_forest, plot_forest
from .send_image_to_clipboard import send_image_to_clipboard


def get_surface():
    """
    Пересчёт подстилающей поверхности и построение сцены.
    """
    Sf = state.Sf
    Tr = state.Tr
    St = state.St

    Kr = [1, 1, 1, 1, 1, 1, 1, 1]
    DOR = [10] * 8
    Type = 4

    FacetN = max(state.Ncr + state.test.Nadir, state.FacetN, 1)

    cMass = np.zeros((13, FacetN))
    cMass[4, :] = 2 * np.pi * np.random.rand(FacetN)
    cMass[5, :] = Type
    cMass[6, :] = Kr[min(Type, 7)]
    cMass[8, :] = np.deg2rad(DOR[min(Type, 7)]) / 2

    FC = np.arange(state.Ncr, FacetN)
    if len(FC) > 0:
        cX = np.random.randn(len(FC))
        cZ = np.random.randn(len(FC))
        cMass[0, FC] = Sf.Dspot * cX + np.mean(Tr.Pos[:-1, 0])
        cMass[2, FC] = Sf.Dspot * cZ + np.mean(Tr.Pos[:-1, 2])
        cMass[1, FC] = 0

    # Построение графика
    fig = plt.figure(figsize=(6, 6), dpi=100)
    ax: Axes3D = fig.add_subplot(111, projection="3d")

    if Tr.Pos.ndim == 2 and Tr.Pos.shape[0] > 0:
        ax.plot3D(Tr.Pos[:, 0], Tr.Pos[:, 2], Tr.Pos[:, 1], "-xm", label="Траектория")

    if St.N > 0 and St.Pos.ndim == 3 and St.Pos.shape[2] >= St.N:
        for n in range(St.N):
            n_pts = St.Pos.shape[0]  # длина траектории
            ax.plot3D(
                St.Pos[:, 0, n],
                St.Pos[:, 2, n],
                np.full(n_pts, 100.0),  # константная высота той же длины
                "-dr",
                label=f"Локатор {n + 1}",
            )

    ax.scatter(
        cMass[0, :], cMass[2, :], cMass[1, :], c="g", s=5, alpha=0.6, label="Surface"
    )

    # Моделирование леса
    if Type == 4:
        forest = get_forest(n_trees=100, area_size=(400, 400), base_height=0)
        plot_forest(forest, ax)

    ax.set_xlabel("x [м]")
    ax.set_ylabel("z [м]")
    ax.set_zlabel("y [м]")
    ax.set_title("Подстилающая поверхность")
    ax.legend()
    ax.grid(True)
    try:
        ax.set_box_aspect([1, 1, 1])
    except Exception:
        pass

    plt.tight_layout()

    # Сохраняем график в буфер
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=100)
    plt.close(fig)
    buf.seek(0)

    # Конвертируем в PIL Image
    pil_img = Image.open(buf)

    # Копируем в буфер обмена
    success = send_image_to_clipboard(pil_img)
    buf.close()

    if success:
        print("✅ График скопирован в буфер обмена.")
    else:
        print("❌ Не удалось скопировать график в буфер обмена.")

    return cMass
