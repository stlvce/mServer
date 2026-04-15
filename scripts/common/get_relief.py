import numpy as np
import os
from typing import Any


def get_relief(
    globals: dict[str, Any] | None = None,
):
    """
    <Название функции>

    Args:
        globals (dict[str, Any]): Глобальные переменные

    Returns:
        tuple[Sf, Relief]
    """

    Sf = globals["Sf"]
    Relief = globals["Relief"]
    # Проверяем существование Relief, и если отсутствует (в Python мы просто проверим, существует ли переменная)
    # Поскольку Python не поддерживает такие же проверки, используем try-except
    # TODO тут поменять
    Sf.XZstep = 10
    Sf.maxY = 100
    Sf.Elev = 25
    Sf.Relief = "Test_cos_relief"
    Sf.Dspot = 100

    # try:
    #     Relief
    # except NameError:
    #     # Инициализация значений в Sf
    #     Sf.XZstep = 10
    #     Sf.maxY = 100
    #     Sf.Elev = 25
    #     Sf.Relief = "Test_cos_relief"
    #     Sf.Dspot = 100

    # Проверка на пустоту и существование Relief
    if Sf.Relief or "Relief" not in globals:
        if Sf.Relief == "peaks":
            Sf.x = Sf.Dspot
            Sf.z = Sf.Dspot
            # Создаем Relief как пиковую поверхность
            Relief = Sf.maxY * 0.5 * np.fromfunction(
                lambda z, x: np.sin(z) * np.cos(x), (Sf.z, Sf.x), dtype=float
            ) + (0.5 - Sf.Elev / 100)

        elif Sf.Relief == "Test_cos_relief":
            Sf.rad_mul = np.pi / 180 / Sf.Dspot * 4
            Sf.n = round(Sf.Dspot)
            Sf.x = Sf.Dspot
            Sf.z = Sf.Dspot
            X = np.ones((Sf.z, 1)) * np.arange(1, Sf.x + 1)
            Z = np.arange(1, Sf.z + 1).reshape(-1, 1) * np.ones((1, Sf.x))
            XZ = X + Z * 1j  # Двумерный массив координат фацетов
            Relief = Sf.maxY * (
                0.5
                * np.cos((np.real(XZ) - (Sf.n + 1) / 2) * Sf.rad_mul)
                * np.cos((np.imag(XZ) - (Sf.n + 1) / 2) * Sf.rad_mul)
                + (0.5 - Sf.Elev / 100)
            )

        else:
            # Загрузка relief из файла
            relief_filepath = os.path.join(os.getcwd(), "relief", Sf.Relief)
            Relief = np.load(
                relief_filepath
            )  # Здесь предполагается, что релief сохранен в .npy файле

        if Sf.maxY > 0:  # Сместим высоты и изменим масштаб
            minY = np.min(Relief)
            difY = np.max(Relief) - minY
            if Sf.maxY == 0:
                Sf.maxY = difY
            Relief = (
                (Relief - minY - difY * (Sf.Elev / 100))
                * (Sf.maxY / difY)
                * 100
                / (100 - Sf.Elev)
            )

            if Sf.Elev > 0:
                Relief[Relief < 0] = 0  # Применим уровень воды в рельефе

        # Параметры массива
        Sf.x_size, Sf.z_size = Relief.shape  # Размеры массива
        Sf.med_shift = min(Sf.x_size, Sf.z_size) / 2 - 0.5  # Смещение

    return Sf, Relief

    # После этого кода можно продолжать работу с `Relief` и `Sf`
