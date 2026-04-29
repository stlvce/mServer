import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

from helpers import save_fig_as_bmp
from state import state

# Маркеры для типов поверхности (индекс = тип)
# 1=грунт, 2=вода, 3=трава, 4=лес, 5=снег/скалы, 6=песок, 7=город, 8=кусты, 9=уголк.отраж.
MARK = {1: "kx", 2: "bo", 3: "g+", 4: "mD", 5: "c^", 6: "yo", 7: "ms", 8: "g*", 9: "vr"}
COLOR = {
    1: "black",
    2: "blue",
    3: "green",
    4: "magenta",
    5: "cyan",
    6: "yellow",
    7: "purple",
    8: "lime",
    9: "red",
}


def get_surface():
    """
    Расчёт поверхности по параметрам.
    Пятно облучения — эллипс, смещённый по тангажу/крену.
    Поддерживаемые типы поверхности:
      1=грунт, 2=вода/волны, 3=трава, 4=лес, 5=снег/скалы,
      6=песок, 7=город, 8=кусты, 9=уголк.отражатели
    """
    Sf = state.Sf
    Tr = state.Tr
    St = state.St
    Sea = state.Sea
    test = state.test

    Type = state.Type if state.Type != 0 else 4
    Ncr = state.Ncr
    FacetN = max(Ncr + test.Nadir, state.FacetN, 1)
    H = float(state.H)
    t = float(state.t)

    # Коэффициенты отражения и ДОР для каждого типа поверхности (индекс = тип, 1-based)
    Kr = [0, 1.0, 0.8, 0.6, 0.5, 0.4, 0.7, 0.9, 0.5, 1.0]  # 0-й не используется
    DOR = [0, 10, 15, 20, 25, 15, 20, 10, 20, 5]
    dH = [0, 0.5, 1.0, 0.3, 8.0, 2.0, 1.0, 5.0, 1.5, 0.0]  # высоты для каждого типа

    # Параметры леса (многоярусный)
    LevNum = 5  # количество ярусов в кронах деревьев
    if (Type == 4) or (Type >= 8):
        LevH = np.array([0.2, 0.4, 0.6, 0.8, 1.0]) * dH[4]  # средние высоты ярусов
        LevdH = np.array([0.7, 0.9, 1.0, 0.8, 0.4]) * LevH  # разброс высот в ярусах
        DORF = (
            np.array([0.7, 0.9, 1.0, 1.2, 1.4]) * np.deg2rad(DOR[4]) / 2
        )  # ДОР ярусов
        KrF = np.array([0.7, 0.9, 1.0, 0.8, 0.4]) * Kr[4]  # коэфф. отражения ярусов
        LevH = np.concatenate([[0], LevH])

    # Углы ориентации ЛА (медиана по всей траектории)
    if Tr.Ang is not None and hasattr(Tr.Ang, "shape") and Tr.Ang.ndim == 2:
        tang = float(np.median(Tr.Ang[:, 0]))  # тангаж, рад
        kren = float(np.median(Tr.Ang[:, 1]))  # крен, рад
    else:
        tang = 0.0
        kren = 0.0

    # Углы отклонения луча
    AnglZ_Prm = np.atleast_1d(state.AnglZ_Prmn)
    AnglX_Prm = np.atleast_1d(state.AnglX_Prmn)
    AnZ = np.deg2rad(float(np.mean(AnglZ_Prm)))  # угол отклонения луча по оси Z
    AnX = np.deg2rad(float(np.mean(AnglX_Prm)))  # угол отклонения луча по оси X

    # Радиус пятна облучения
    # DNA1/DNA2 — ширина ДНА (используем Sf.Dspot из state или вычисляем)
    if hasattr(Sf, "Dspot") and Sf.Dspot != 0:
        pass  # уже задан
    else:
        Sf.Dspot = np.tan(np.deg2rad(10)) * H  # заглушка: 10 градусов

    if state.ChannelN > 1:
        # Если более одного канала — центруем пятно в подрадарную точку
        Sf.Dspot = Sf.KspotN * H  # диаметр пятна облучения

    # Координата центра "эффективного" луча с учётом тангажа и крена
    Rxs = H * np.tan(AnX + tang) * 0.5  # X центра луча
    Rzs = H * np.tan(AnZ + kren) * 0.5  # Z центра луча

    # Угол-азимут направления луча и коэффициент расширения эллипса
    AnD = np.angle(Rxs + 1j * Rzs)  # направление луча
    AnK = 1 + abs(Rxs + 1j * Rzs) / max(Sf.Dspot, 1e-9)  # коэфф. расширения пятна

    # Координаты центра луча с учётом смещения траектории
    Xc1 = Rxs + float(np.mean(Tr.Pos[:-1, 0]))  # X центра луча
    Zc1 = Rzs + float(np.mean(Tr.Pos[:-1, 2]))  # Z центра луча

    # ---- Инициализация массива параметров фацетов ----
    # cMass[0,:]=X, [1,:]=Y, [2,:]=Z, [3,:]=?,
    # [4,:]=фаза, [5,:]=тип, [6,:]=Kr, [7,:]=Vx, [8,:]=ДОР,
    # [9,:]=DOR, [10,:]=наклон X, [11,:]=наклон Z, [12,:]=?
    cMass = np.zeros((13, FacetN))
    cMass[4, :] = 2 * np.pi * np.random.rand(FacetN)  # случайный фазовый сдвиг
    cMass[5, :] = Type  # изначальный тип поверхности
    cMass[6, :] = Kr[min(Type, 8)]  # коэффициент отражения
    cMass[8, :] = np.deg2rad(DOR[min(Type, 8)]) / 2  # ДОР

    Q = 150 / max(1, np.log10(FacetN))  # множитель размера маркера

    # ---- Уголковые отражатели ----
    # test.Xcr/Zcr могут быть строковыми выражениями вида '1*H*cos((nr-1)*45*pi/180)'
    # Вычисляем через evs с nr как массивом индексов уголковых отражателей
    def _eval_cr(expr, nr_arr):
        """Вычисляет выражение уголкового отражателя для массива индексов nr."""
        from state import evs as _evs

        if isinstance(expr, str):
            import numpy as _np

            ctx = {k: v for k, v in vars(state).items() if isinstance(v, (int, float))}
            ctx.update(
                {
                    "nr": nr_arr,
                    "Ncr": Ncr,
                    "H": H,
                    "cos": _np.cos,
                    "sin": _np.sin,
                    "tan": _np.tan,
                    "sqrt": _np.sqrt,
                    "pi": _np.pi,
                    "deg2rad": _np.deg2rad,
                }
            )
            expr_py = (
                expr.replace(".*", "*")
                .replace("./", "/")
                .replace(".^", "**")
                .replace("^", "**")
            )
            try:
                return eval(expr_py, {"__builtins__": {}}, ctx)
            except Exception:
                return float(_evs(expr))
        return float(expr)

    if Ncr + test.Nadir > 0:
        if Ncr > 0:
            nr_arr = np.arange(1, Ncr + 1)  # nr = 1:Ncr как в MATLAB
            cMass[0, :Ncr] = _eval_cr(test.Xcr, nr_arr) + Tr.Pos[0, 0]  # X координата
            cMass[2, :Ncr] = _eval_cr(test.Zcr, nr_arr) + Tr.Pos[0, 2]  # Z координата
        if test.Nadir > 0:
            cMass[0, Ncr + test.Nadir - 1] = Tr.Pos[0, 0]  # X координата надирного
            cMass[2, Ncr + test.Nadir - 1] = Tr.Pos[0, 2]  # Z координата надирного
        cMass[5, : Ncr + test.Nadir] = 9  # тип: 9=уголковые отражатели
        cMass[6, : Ncr + test.Nadir] = 1  # коэффициент отражения
        cMass[8, : Ncr + test.Nadir] = 1  # ДОР для уголкового отражателя

    # ---- Генерация фацетной плоскости (остальные отражатели) ----
    if FacetN > Ncr + test.Nadir:
        FC_len = FacetN - Ncr - test.Nadir
        FC_idx = np.arange(FC_len)  # локальные индексы

        if FacetN % 100 == 1:
            # Спиральное расположение фацетов
            cA_amp = np.linspace(1, 0, FC_len)  # амплитуды
            cA_phi = np.linspace(-6 * 2 * np.pi, 0, FC_len)  # фазы
        else:
            # Случайное расположение фацетов в эллиптическом пятне облучения
            cA_amp = np.sqrt(np.random.rand(FC_len))  # амплитуды
            cA_phi = np.random.rand(FC_len) * 2 * np.pi  # фазы

        # Формирование эллипса с учётом направления и расширения луча
        cA = cA_amp * (np.cos(cA_phi) * AnK + 1j * np.sin(cA_phi))
        cA = cA * (np.cos(AnD) + 1j * np.sin(AnD))  # поворот эллипса вдоль луча

        cX = np.real(cA)
        cZ = np.imag(cA)

        FC_global = np.arange(Ncr + test.Nadir, FacetN)
        cMass[0, FC_global] = Sf.Dspot * cX + Xc1  # X координата
        cMass[2, FC_global] = Sf.Dspot * cZ + Zc1  # Z координата

    # ---- Подготовка графика ----
    fig = plt.figure(figsize=(8, 8), dpi=100)
    ax = fig.add_subplot(111, projection="3d")
    legend_labels = []

    # Траектория РЛС
    if state.test.SwT if hasattr(state.test, "SwT") else True:
        if Tr.Pos.ndim == 2 and Tr.N > 0:
            m_idx = (
                np.round(np.linspace(0, Tr.N - 1, 11)).astype(int)
                if Tr.N > 200
                else np.arange(Tr.N)
            )
            ax.plot(Tr.Pos[m_idx, 0], Tr.Pos[m_idx, 2], Tr.Pos[m_idx, 1], "-xm")
            legend_labels.append("Траект.ЛА")

        # Траектории целей
        if St.N > 0 and St.Pos.ndim == 3:
            for cnt in range(St.N):
                ax.plot(
                    St.Pos[m_idx, 0, cnt],
                    St.Pos[m_idx, 2, cnt],
                    St.Pos[m_idx, 1, cnt],
                    "-dr",
                )
                legend_labels.append(f"Траект.Ц.{cnt + 1}")

    Sf.Types = np.zeros(10, dtype=int)
    Sf.Types[9] = Ncr + test.Nadir

    # ---- Обработка типов поверхности ----

    # Тип 4: Лес
    FC = np.where(cMass[5, :] == 4)[0]
    Sf.Types[4] = len(FC)
    if len(FC) > 0:
        print(f"4forest:{Sf.Types[4]}, ", end="")
        if hasattr(Sf, "TreeT") and Sf.TreeT == 1:
            # Хвойный лес
            cMass[1, FC] = dH[4] * (np.random.rand(len(FC)) * 0.9 + 0.1)
        elif hasattr(Sf, "TreeT") and Sf.TreeT < 5:
            # Лиственный/смешанный лес
            cMass[1, FC] = dH[4] * (
                np.abs(np.random.rand(len(FC)) + 1j * np.random.rand(len(FC))) * 0.5
                + 0.29289
            )
        else:
            # Многоярусный лес
            LevCount = np.random.randint(0, LevNum, size=len(FC))
            cMass[1, FC] = (
                cMass[1, FC]
                + np.random.rand(len(FC)) * LevdH[LevCount]
                + LevH[LevCount + 1]
            )  # Y верх леса
            cMass[6, FC] = KrF[LevCount] * np.random.randn(len(FC))  # коэфф. отражения
            cMass[7, FC] = (
                Sf.WindV * np.cosd(Sf.WindTh) * np.random.randn(len(FC))
            )  # Vx по ветру
            cMass[8, FC] = (
                Sf.WindV * np.sind(Sf.WindTh) * np.random.randn(len(FC))
            )  # Vz по ветру
            cMass[9, FC] = DORF[LevCount]  # ДОР ярусов

        ax.scatter(
            cMass[0, FC],
            cMass[2, FC],
            cMass[1, FC],
            s=np.abs(cMass[6, FC] * cMass[9, FC] * Q + 10),
            c=COLOR[4],
            marker="D",
            alpha=0.6,
        )
        legend_labels.append("Лес(крона)")

    # Тип 7: Город/дорога
    FC = np.where(cMass[5, :] == 7)[0]
    Sf.Types[7] = len(FC)
    if len(FC) > 0:
        TownD = Sf.TownD if hasattr(Sf, "TownD") else 10
        # Прямоугольная форма зданий
        cMass[1, FC] = np.abs(
            np.round(cMass[0, FC] * TownD * 0.01) / dH[7]
            + 0.5
            - np.round(cMass[0, FC] * TownD * 0.01 / dH[7] + 0.5)
        ) + np.abs(
            np.round(cMass[2, FC] / dH[7]) * 0.3333
            - np.round(cMass[2, FC] / dH[7] * 0.3333)
        )
        # Оставляем только крыши зданий (высота выше 33%)
        low = np.where((cMass[5, :] == 7) & (cMass[1, :] < 0.667))[0]
        cMass[5, low] = 1  # остальные -> грунт
        FC = np.where(cMass[5, :] == 7)[0]
        Sf.Types[7] = len(FC)
        if len(FC) > 0:
            print(f"7town:{Sf.Types[7]}, ", end="")
            cMass[1, FC] = cMass[1, FC] * dH[7] * 1.2  # высота крыш зданий
            cMass[6, FC] = Kr[7]
            cMass[8, FC] = np.deg2rad(DOR[7]) / 2
            ax.stem(
                cMass[0, FC],
                cMass[2, FC],
                cMass[1, FC],
                markerfmt=MARK[7],
                linefmt="m-",
                basefmt=" ",
            )
            legend_labels.append("Город/дорога")

    # Тип 1: Грунт/пашня
    FC = np.where(cMass[5, :] == 1)[0]
    Sf.Types[1] = len(FC)
    if len(FC) > 0:
        print(f"1ground:{Sf.Types[1]}, ", end="")
        # Рельеф "холмы и впадины" — длина холма = 20 высот
        cMass[1, FC] = (
            0.5
            * dH[1]
            * np.sin(np.pi * 0.25 * cMass[0, FC] / dH[1])
            * np.cos(np.pi * 0.25 * cMass[2, FC] / dH[1])
        )
        cMass[6, FC] = Kr[1]
        cMass[8, FC] = np.deg2rad(DOR[1]) / 2
        ax.scatter(
            cMass[0, FC],
            cMass[2, FC],
            cMass[1, FC],
            s=np.abs(cMass[6, FC]) * cMass[8, FC] * Q,
            c=COLOR[1],
            marker="x",
            alpha=0.7,
        )
        legend_labels.append("Грунт/пашня")

    # Тип 2: Вода/волны — эллипс пятна с учётом морского волнения
    FC = np.where(cMass[5, :] == 2)[0]
    Sf.Types[2] = len(FC)

    Sea.WaveL = dH[1] * 5

    if len(FC) > 0:
        print(f"2water:{Sf.Types[2]}, ", end="")
        WindV = Sf.WindV if hasattr(Sf, "WindV") else 0
        WindTh = Sf.WindTh if hasattr(Sf, "WindTh") else 0
        WaveL = (
            Sea.WaveL if Sea.WaveL > 0 else max(WindV**2 / 9.8, 1.0)
        )  # длина волны по ветру
        Shift = Sea.Shift if hasattr(Sea, "Shift") else 0

        # Вектор движения волны вдоль направления ветра
        Vec = cMass[0, FC] * np.sin(np.deg2rad(WindTh)) - cMass[2, FC] * np.cos(
            np.deg2rad(WindTh)
        )
        # Фаза движения волны (1.25 = sqrt(g/2pi))
        Arg = 2 * np.pi * Vec / WaveL + np.deg2rad(Shift) + t * np.sqrt(WaveL) * 1.25

        cMass[1, FC] = 0.5 * dH[2] * np.cos(Arg)  # Y координата
        cMass[7, FC] = WindV * np.cos(np.deg2rad(WindTh)) / 100  # Vx воды
        cMass[8, FC] = WindV * np.sin(np.deg2rad(WindTh)) / 100  # Vz воды
        cMass[9, FC] = np.deg2rad(DOR[2]) / 2  # ДОР
        # Угол наклона оси ДОР к нормали (зависит от фазы волны и направления ветра)
        cMass[10, FC] = (
            np.sin(Arg) * np.sin(np.deg2rad(WindTh)) * dH[2] / WaveL
        )  # наклон по X
        cMass[11, FC] = (
            np.cos(Arg) * np.cos(np.deg2rad(WindTh)) * dH[2] / WaveL
        )  # наклон по Z
        cMass[6, FC] = Kr[2] * cMass[10, FC]  # коэфф. отражения

        ax.scatter(
            cMass[0, FC],
            cMass[2, FC],
            cMass[1, FC],
            s=np.abs(cMass[6, FC]) * cMass[9, FC] * Q + 1,
            c=COLOR[2],
            marker="o",
            alpha=0.6,
        )
        legend_labels.append("Water surf.")

    # Тип 3: Трава
    FC = np.where(cMass[5, :] == 3)[0]
    Sf.Types[3] = len(FC)
    if len(FC) > 0:
        print(f"3grass:{Sf.Types[3]}, ", end="")
        WindV = Sf.WindV if hasattr(Sf, "WindV") else 0
        WindTh = Sf.WindTh if hasattr(Sf, "WindTh") else 0
        cMass[1, FC] = (
            cMass[1, FC] + (1 + 0.5 * np.random.randn(len(FC))) * dH[3]
        )  # Y координата
        cMass[6, FC] = Kr[3] * np.random.randn(len(FC))  # коэфф. отражения
        cMass[7, FC] = (
            WindV * np.cos(np.deg2rad(WindTh)) * np.random.randn(len(FC))
        )  # Vx травы
        cMass[8, FC] = (
            WindV * np.sin(np.deg2rad(WindTh)) * np.random.randn(len(FC))
        )  # Vz травы
        cMass[9, FC] = np.deg2rad(DOR[3]) / 2  # ДОР
        ax.scatter(
            cMass[0, FC],
            cMass[2, FC],
            cMass[1, FC],
            s=5,
            c=COLOR[3],
            marker="+",
            alpha=0.7,
        )
        legend_labels.append("Трава")

    # Тип 5: Снег/скалы/лёд
    FC = np.where(cMass[5, :] == 5)[0]
    Sf.Types[5] = len(FC)
    if len(FC) > 0 and Type == 5:
        # Двухслойный лёд: верх и низ
        FC1 = FC[::2]  # верх льда
        FC2 = FC[1::2]  # низ льда
        print(f"5icetop+bed:{len(FC1)}+{len(FC2)}, ", end="")
        cMass[1, FC1] = dH[5]  # Y верх льда
        cMass[9, FC] = np.deg2rad(DOR[5]) / 2  # ДОР верх льда
        ax.scatter(
            cMass[0, FC1],
            cMass[2, FC1],
            cMass[1, FC1],
            s=np.abs(cMass[6, FC1]) * cMass[9, FC1] * Q * 10,
            c=COLOR[5],
            marker="^",
            alpha=0.7,
        )
        legend_labels.append("Верх льда")
        cMass[5, FC2] = 2  # тип: низ льда -> вода
        cMass[1, FC2] = -dH[2]  # Y низ льда
        cMass[9, FC2] = np.deg2rad(DOR[2]) / 2  # ДОР низ льда
        ax.scatter(
            cMass[0, FC2],
            cMass[2, FC2],
            cMass[1, FC2],
            s=np.abs(cMass[6, FC2]) * cMass[9, FC2] * Q,
            c=COLOR[2],
            marker="o",
            alpha=0.5,
        )
        legend_labels.append("Низ льда")
    elif len(FC) > 0:
        print(f"5mounts:{Sf.Types[5]}, ", end="")
        cMass[1, FC] = (
            cMass[1, FC] + (1 + 0.5 * np.random.randn(len(FC))) * dH[5]
        )  # Y координата
        cMass[6, FC] = Kr[5] * np.random.randn(len(FC))  # коэфф. отражения
        cMass[9, FC] = np.deg2rad(DOR[5]) / 2  # ДОР скал
        ax.scatter(
            cMass[0, FC],
            cMass[2, FC],
            cMass[1, FC],
            s=np.abs(cMass[6, FC]) * cMass[9, FC] * Q,
            c=COLOR[5],
            marker="^",
            alpha=0.7,
        )
        legend_labels.append("Снег/скалы")

    # Тип 6: Песок/солончак
    FC = np.where(cMass[5, :] == 6)[0]
    Sf.Types[6] = len(FC)
    if len(FC) > 0:
        print(f"6sand:{Sf.Types[6]}, ", end="")
        cMass[1, FC] = (
            cMass[1, FC] + (1 + 0.5 * np.random.randn(len(FC))) * dH[6]
        )  # Y координата
        cMass[6, FC] = Kr[6] * np.random.randn(len(FC))  # коэфф. отражения
        cMass[9, FC] = np.deg2rad(DOR[6]) / 2  # ДОР солончак
        ax.scatter(
            cMass[0, FC],
            cMass[2, FC],
            cMass[1, FC],
            s=np.abs(cMass[6, FC]) * cMass[9, FC] * Q,
            c=COLOR[6],
            marker="o",
            alpha=0.7,
        )
        legend_labels.append("Песок/солончак")

    # Тип 8: Кусты
    FC = np.where(cMass[5, :] == 8)[0]
    Sf.Types[8] = len(FC)
    if len(FC) > 0:
        print(f"8bushes:{Sf.Types[8]}, ", end="")
        WindV = Sf.WindV if hasattr(Sf, "WindV") else 0
        WindTh = Sf.WindTh if hasattr(Sf, "WindTh") else 0
        cMass[1, FC] = (
            cMass[1, FC] + (1 + 0.5 * np.random.randn(len(FC))) * dH[8]
        )  # Y координата
        cMass[6, FC] = Kr[8] * np.random.randn(len(FC))  # коэфф. отражения
        cMass[9, FC] = np.deg2rad(DOR[8]) / 2  # ДОР кустарник
        ax.scatter(
            cMass[0, FC],
            cMass[2, FC],
            cMass[1, FC],
            s=np.abs(cMass[6, FC]) * cMass[9, FC] * Q,
            c=COLOR[8],
            marker="*",
            alpha=0.7,
        )
        legend_labels.append("Кусты/прочее")

    # Тип 9: Уголковые отражатели
    print(f"9уг.отр:{Sf.Types[9]}")
    FC = np.arange(Ncr + test.Nadir)
    if len(FC) > 0:
        ax.plot(cMass[0, FC], cMass[2, FC], cMass[1, FC], "-vr")
        legend_labels.append("Уголк.отраж.")

    # ---- Оформление графика ----
    ax.set_xlabel("x (м)", fontsize=9)
    ax.set_ylabel("z (м)", fontsize=9)
    ax.set_zlabel("y (м)", fontsize=9)
    ax.grid(True)
    try:
        ax.set_box_aspect([1, 1, 1])
    except Exception:
        pass
    if legend_labels:
        ax.legend(legend_labels, loc="upper right", fontsize=8)
    if hasattr(state.test, "SwT") and state.test.SwT:
        ax.set_title(
            "Траектория движения и поверхность", fontsize=9, fontweight="normal"
        )
    else:
        ax.set_title("Поверхность (пятно облучения)", fontsize=9, fontweight="normal")

    plt.tight_layout()
    save_fig_as_bmp("resultFig3.bmp")

    return cMass
