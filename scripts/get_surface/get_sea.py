import numpy as np
from scipy.spatial.transform import Rotation as Rot
from typing import Any


def get_sea(
    globals: dict[str, Any] | None = None,
):
    """
    <Название функции>

    Args:
        globals (dict[str, Any]): Глобальные переменные
    """

    Sea = globals["Sea"]
    Sf = globals["Sf"]
    g = globals["g"]  # TODO нет в init_variable
    t = globals["t"]

    # Предполагается, что переменные Sf, Sea, consts, cMass, t уже определены
    # Если FC не определен, задаем его как все индексы столбцов cMass
    if "FC" not in globals():
        cMass = globals["cMass"]  # TODO нет в init_variable
        FC = np.arange(cMass.shape[1])  # TODO нет в init_variable

    # Преобразуем углы в радианы и вычисляем вектор ветра
    wind_ang = np.deg2rad([Sf["WindFi"], Sf["WindTh"], 0])
    rot_mat = Rot.from_euler("xyz", wind_ang).as_matrix()
    Sea.WindVec = rot_mat.dot(
        np.array([0, round(Sf["WindV"]), 0])
    )  # TODO нет в init_variable
    # TODO нет в init_variable
    Sea.U10 = np.linalg.norm(Sea["WindVec"])  # скорость ветра на высоте 10 м
    Sea.WindV = np.array([0, Sf["WindV"], 0])

    # Доопределение параметров поверхности по силе ветра
    wind_speed = np.floor(np.abs(Sf["WindV"]))
    if wind_speed <= 1:
        Sea.update(
            {
                "strenght": "1B",
                "kb": 0.008,
                "fl": 1e3,
                "fs": 0.06,
                "fe": 0.7,
                "trk": 0.0001,
            }
        )
    elif wind_speed <= 3:
        Sea.update(
            {
                "strenght": "2B",
                "kb": 0.03,
                "fl": 1e3,
                "fs": 0.02,
                "fe": 0.2,
                "trk": 0.01,
            }
        )
    elif wind_speed == 4:
        Sea.update(
            {
                "strenght": "3B",
                "kb": 0.35,
                "fl": 1e3,
                "fs": 0.29,
                "fe": 0.8,
                "trk": 0.18,
            }
        )
    elif wind_speed == 5:
        Sea.update(
            {
                "strenght": "3B",
                "kb": 0.588,
                "fl": 2e3,
                "fs": 0.25,
                "fe": 1.6,
                "trk": 0.2,
            }
        )
    elif wind_speed == 6:
        Sea.update(
            {
                "strenght": "4B",
                "kb": 0.6,
                "fl": 5e3,
                "fs": 0.23,
                "fe": 1.57,
                "trk": 0.17,
            }
        )
    elif wind_speed == 7:
        Sea.update(
            {"strenght": "4B", "kb": 0.6, "fl": 7e3, "fs": 0.20, "fe": 1.2, "trk": 0.18}
        )
    elif wind_speed == 8:
        Sea.update(
            {"strenght": "4B", "kb": 0.5, "fl": 9e3, "fs": 0.20, "fe": 1.2, "trk": 0.21}
        )
    elif wind_speed == 9:
        Sea.update(
            {
                "strenght": "5B",
                "kb": 0.6,
                "fl": 11e3,
                "fs": 0.18,
                "fe": 1.0,
                "trk": 0.25,
            }
        )
    elif wind_speed == 10:
        Sea.update(
            {
                "strenght": "5B",
                "kb": 0.6,
                "fl": 12e3,
                "fs": 0.14,
                "fe": 1.8,
                "trk": 0.20,
            }
        )
    elif wind_speed == 11:
        Sea.update(
            {
                "strenght": "6B",
                "kb": 0.9,
                "fl": 37e3,
                "fs": 0.12,
                "fe": 1.8,
                "trk": 0.30,
            }
        )
    elif wind_speed == 12:
        Sea.update(
            {
                "strenght": "6B",
                "kb": 0.62,
                "fl": 40e3,
                "fs": 0.13,
                "fe": 0.7,
                "trk": 0.35,
            }
        )
    elif wind_speed == 13:
        Sea.update(
            {
                "strenght": "6B",
                "kb": 0.4,
                "fl": 42e3,
                "fs": 0.18,
                "fe": 0.6,
                "trk": 0.35,
            }
        )
    elif wind_speed == 14:
        Sea.update(
            {
                "strenght": "7B",
                "kb": 0.38,
                "fl": 46e3,
                "fs": 0.17,
                "fe": 0.55,
                "trk": 0.55,
            }
        )
    elif wind_speed == 15:
        Sea.update(
            {
                "strenght": "7B",
                "kb": 0.38,
                "fl": 27e3,
                "fs": 0.17,
                "fe": 0.62,
                "trk": 0.35,
            }
        )
    elif wind_speed == 16:
        Sea.update(
            {
                "strenght": "7B",
                "kb": 0.38,
                "fl": 48e3,
                "fs": 0.19,
                "fe": 0.54,
                "trk": 0.55,
            }
        )
    elif wind_speed == 17:
        Sea.update(
            {
                "strenght": "8B",
                "kb": 0.35,
                "fl": 50e3,
                "fs": 0.22,
                "fe": 0.59,
                "trk": 0.55,
            }
        )
    elif wind_speed == 18:
        Sea.update(
            {
                "strenght": "8B",
                "kb": 0.45,
                "fl": 62e3,
                "fs": 0.16,
                "fe": 0.54,
                "trk": 0.45,
            }
        )
    elif wind_speed == 19:
        Sea.update(
            {
                "strenght": "8B",
                "kb": 0.55,
                "fl": 135e3,
                "fs": 0.15,
                "fe": 0.45,
                "trk": 0.45,
            }
        )
    else:  # wind_speed >= 20
        Sea.WindV = np.array([0, 20, 0])
        Sea.update(
            {
                "strenght": "9B",
                "kb": 0.45,
                "fl": 150e3,
                "fs": 0.17,
                "fe": 0.67,
                "trk": 0.3,
            }
        )

    # Спектр волны
    if Sf["WindV"] < 4:
        # Капиллярные волны
        Sea["st"] = 0.0757 * (1 - Sf["AirT"] / 374) ** (9 / 11)
        gamm = Sea["st"] * Sea["rho"]
        beta = 1 / Sea["nr"]
        Sea["F"] = np.linspace(Sea["fs"], Sea["fe"], Sea["nr"])
        S = beta * gamm ** (-2 / 3) * (2 * np.pi * Sea["F"]) ** (-7 / 3)
        Sea["H"] = np.sqrt(S)
        Sea["L"] = 2 * np.pi * Sea["H"]
    else:
        # TMA спектр
        Sea["st"] = 0.0757 * (1 - Sf["AirT"] / 374) ** (9 / 11)
        gamm = 3.3
        beta = 1.25
        fp = 3.5 * (g**2 * Sea["fl"] * Sea["U10"] ** (-3)) ** (-0.33)

        # Разбиение частотного диапазона
        fa = int(Sea["nr"] * (fp - Sea["fs"]) / (Sea["fe"] - Sea["fs"]))
        fb = Sea["nr"] - fa
        Sea["F"] = np.concatenate(
            [np.linspace(Sea["fs"], fp, fa), np.linspace(fp, Sea["fe"], fb)]
        )

        # Расчет спектральной плотности
        Sigma = np.where(Sea["F"] <= fp, 0.07, 0.09)
        r = np.exp(-0.5 * ((Sea["F"] - fp) / (fp * Sigma)) ** 2)
        alpha = 0.076 * (Sea["U10"] ** 2 / Sea["fl"] / g) ** 0.22
        S = (
            alpha
            * g**2
            * (2 * np.pi) ** -4
            * Sea["F"] ** -5
            * np.exp(-beta * (fp / Sea["F"]) ** 4)
            * gamm**r
        )

        # Поправка на глубину
        F_ = Sea["F"] * np.sqrt(Sea["depth"] / g)
        K = 2 * F_**2 * np.tanh((2 * np.pi * F_) ** 2 * Sea["depth"])
        S_ = 1 / np.tanh(K)
        Fi = (1 + K / np.sinh(K)) * S_
        S *= Fi

        # Расчет высоты волн
        kappa = 1
        Sea["H"] = np.sqrt(S * g**2 / (8 * kappa * Sea["F"] ** 3))

        # Расчет длины волны
        lev = 0.5
        Sea["L"] = np.where(Sea["H"] >= lev, 1.5 / (Sea["F"] ** 2), Sea["H"])

    # Финализация параметров волн
    Sea["nr"] = len(Sea["H"])
    Sea["K"] = 2 * np.pi / Sea["L"]  # Волновое число
    Sea["G"] = g + Sea["st"] / Sea["rho"] * Sea["K"] ** 2
    Sea["W"] = np.sqrt(
        Sea["G"] * Sea["K"] * np.tanh(Sea["K"] * Sea["depth"])
    )  # Угловые частоты
    Sea["V_wave"] = (
        Sea["H"] ** 2 * (2 * np.pi / Sea["L"]) ** 2 * Sea["W"]
    )  # Скорости волн
    Sea["Fi0"] = np.random.uniform(-np.pi, np.pi, Sea["nr"])  # Случайные фазы

    # Направления волн с учетом ветра
    dir_base = np.random.uniform(-np.pi, np.pi, Sea["nr"])
    Sea["Dir"] = dir_base * np.exp(-0.1 * Sea["H"]) * Sea["kb"] - np.pi + Sf["WindFi"]

    # Формирование поверхности
    X = cMass[0, FC]
    Y = cMass[2, FC]
    Z = np.zeros_like(X)

    for n in range(Sea["nr"]):
        D = (X - Sea["V_wave"][n] * t) * np.cos(Sea["Dir"][n]) + (
            Y - Sea["V_wave"][n] * t
        ) * np.sin(Sea["Dir"][n])
        Sin = np.sin(Sea["K"][n] * D - Sea["W"][n] * t + Sea["Fi0"][n])

        if Sf["WindV"] < 4:
            Z += Sea["H"][n] * Sin
        else:
            CC = 1 / (1 - np.exp(-Sea["trk"] * Sea["H"][n]))
            CA = Sea["H"][n] * (CC**2 - 1)
            CB = -CC * Sea["H"][n]
            Z += CA / (CC + Sin) + CB + Sea["H"][n] * Sin

    # Нормировка и центрирование
    valid_waves = np.sum(Sea["H"] > 0.97 * np.max(Sea["H"]))
    if valid_waves > 0:
        Z /= valid_waves
    Z -= np.mean(Z)

    # Обновление координат Z в матрице масс
    cMass[1, FC] = Z
