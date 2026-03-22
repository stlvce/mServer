import numpy as np
from state import state


def set_mi_param():
    """
    Установка параметров-настройки МИ.
    Расчёт относительных мощностей излучателей МИ.

    На входе значения КЦО от -50 до +50, например Mi.z=21; Mi.y=-18;
    а также Mi.dx=? по умолчанию 1м, Mi.dz=? по умолчанию 1м,
    а также, если все Изл.МИ включены, то Mi.a = [1, 1, 1, 1]
    """

    try:
        state.Mi.Z = np.array([50, -50, 0, 0], dtype=float)  # Mi.X=[-50, 50, 0, 0]
        state.Mi.Y = np.array([0, 0, 50, -50], dtype=float)  # Mi.Z=[0, 0, -50, 50]

        # Mi.z=25; Mi.y=25; # строка только для отладки

        tmpa = np.abs(state.Mi.Z + state.Mi.Y - state.Mi.z - state.Mi.y) / np.sqrt(2)
        tmpd = np.sqrt((state.Mi.Z - state.Mi.z) ** 2 + (state.Mi.Y - state.Mi.y) ** 2)

        # Расчёт относительных мощностей
        state.Mi.Pi = state.Mi.a * tmpa * np.sqrt(np.maximum(tmpd**2 - tmpa**2, 0)) / 50

    except Exception:
        # Доопределяем параметры на случай 1-го запуска до определения всех параметров
        state.Mi.z = 0
        state.Mi.y = 0
        state.Mi.a = np.array([1, 1, 1, 1], dtype=float)
        state.Mi.Pi = np.array([1, 1, 1, 1], dtype=float)
