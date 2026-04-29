import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

from helpers import save_fig_as_bmp
from state import evs, state


def _evs_local(path: str, **extra) -> float:
    """
    Вычисляет строковое выражение из поля state с дополнительным локальным контекстом.
    Например: _evs_local('Rs.Timp', tauimp=1e-8, Sqw=4) -> вычислит 'tauimp*Sqw' = 4e-8
    """
    # Получаем значение поля
    parts = path.split(".")
    if len(parts) == 2:
        obj = getattr(state, parts[0], None)
        val = getattr(obj, parts[1], None) if obj else None
    else:
        val = getattr(state, path, None)

    if val is None:
        return 0.0

    # Если не строка — сразу возвращаем как float
    if not isinstance(val, str):
        return float(val)

    # Строковое выражение — добавляем локальные переменные в контекст evs
    # Сначала пробуем через стандартный evs
    result = evs(val)
    if isinstance(result, (int, float)):
        return float(result)

    # Если evs не справился — пробуем с дополнительным контекстом
    ctx = {k: v for k, v in vars(state).items() if isinstance(v, (int, float))}
    ctx.update(extra)  # добавляем локальные переменные (tauimp, Sqw и т.д.)
    try:
        return float(eval(val, {"__builtins__": {}}, ctx))
    except Exception:
        return 0.0


def get_traekt():
    """
    Расчёт точек в траектории по параметрам.
    Tr.V в м/с (а не в длинах волн * м/с).
    Используем evs() для вычисления вводимых переменных параметров.
    """
    Tr = state.Tr
    St = state.St
    Rs = state.Rs

    Nimp = int(Rs.Nimp)

    # Параметры сигнала в зависимости от режима (Ym==0 — импульсный, Ym>0 — ЛЧМ)
    if state.Ym == 0:
        tauimp = _evs_local("Rs.tauimp")
        Sqw = float(state.Sqw) if state.Sqw != 0 else 1  # защита от деления на 0
        Timp = _evs_local("Rs.Timp", tauimp=tauimp, Sqw=Sqw)
        dtau = _evs_local("Rs.dtau", tauimp=tauimp)
        Rs.Tm = Timp
        Tm = Timp
        Rs.dR = dtau * state.c  # шаг по дальности
    else:
        Tm = _evs_local("Rs.Tm")

    snr = float(evs("Rs.snr")) if isinstance(Rs.snr, str) else float(Rs.snr)  # noqa: F841

    # Средняя длина волны
    if state.f0n != 0:
        Rs.Lambda = state.c / state.f0n

    state.test.canceling = 0
    perc_mem = -1  # процент выполнения для вывода по UDP

    n = list(range(St.N))  # счётчик для всех целей

    # Инициализируем траекторию (при первом запуске или обновлении параметров РЛС)
    Tr.H1 = state.H
    Tr.N = Nimp

    # Подготовим массивы описания траектории (N+1 точка для корректного расчёта фаз)
    Tr.t = np.zeros(Tr.N + 1)  # время в модели
    Tr.Pos = np.zeros((Tr.N + 1, 3))  # позиции (x, h, z)
    Tr.V = np.zeros((Tr.N, 3))  # вектор скорости
    Tr.Ang = np.zeros((Tr.N, 3))  # углы ориентации осей ЛА
    Tr.Tm = np.zeros(Tr.N)  # период модуляции/повторения импульсов
    Tr.Ti = np.zeros(Tr.N)  # длительность зондирующего импульса
    Tr.Tm_Ni = np.zeros(Tr.N)  # число полупериодов в периоде (импульсов в пачке)
    Tr.Tm_i = np.zeros(Tr.N)  # номер текущего полупериода в периоде
    Tr.TiT = np.zeros(Tr.N)
    Tr.TiR = np.zeros(Tr.N)
    Tr.Pz = np.zeros(Tr.N)  # мощность передатчика (может зависеть от высоты)

    # Начальная позиция РЛС (x, h, z)
    Tr.Pos[0, :] = [float(evs("Tr.Xa")), float(evs("Tr.Ya")), float(evs("Tr.Za"))]

    # Инициализируем траектории целей
    St.Pos = np.zeros((Tr.N + 1, 3, St.N))
    St.V = np.zeros((Tr.N, 3, St.N))
    St.Ang = np.zeros((Tr.N, 3, St.N))

    if St.N > 0:
        for ni in n:
            St.Pos[0, 0, ni] = float(evs("St.Xs"))  # начальная позиция x
            St.Pos[0, 1, ni] = float(evs("St.Ys"))  # начальная позиция h
            St.Pos[0, 2, ni] = float(evs("St.Zs"))  # начальная позиция z

    # Проверяем нужно ли пересчитывать скорости или брать фиксированные позиции
    TrVskip = (
        str(state.Tr.Vx) == "0" and str(state.Tr.Vy) == "0" and str(state.Tr.Vz) == "0"
    )
    StVskip = (
        str(state.St.Vx) == "0" and str(state.St.Vy) == "0" and str(state.St.Vz) == "0"
    )

    Ni = 1  # число полупериодов в периоде (будет обновляться)
    t = float(
        str(state.t).strip("()")
    )  # текущее время в модели (убираем скобки если строка)

    # ==== Расчёт точек траектории ====
    for m in range(1, Tr.N + 2):  # N+1 точка траектории
        # Отправка прогресса (процент выполнения)
        perc = round(100 * (m - 1) / (Tr.N + 1))
        if perc > perc_mem:
            perc_mem = perc
            print(f"Percent={perc}")  # отправляется по UDP в ПО SamRLSim

        idx = m - 1  # 0-based индекс
        Tr.t[idx] = t  # текущее время в модели

        if m > 1:
            dT = t - Tr.t[idx - 1]  # время от предыдущего положения, с

            # Расчёт позиции РЛС
            if TrVskip:
                Tr.Pos[idx, :] = [
                    float(evs("Tr.Xa")),
                    float(evs("Tr.Ya")),
                    float(evs("Tr.Za")),
                ]
            else:
                # Сдвигаем по вектору скорости
                Tr.Pos[idx, :] = Tr.Pos[idx - 1, :] + Tr.V[idx - 1, :] * dT

            # Расчёт позиций целей
            if St.N > 0:
                if StVskip:
                    for ni in n:
                        St.Pos[idx, :, ni] = [
                            float(evs("St.Xs")),
                            float(evs("St.Ys")),
                            float(evs("St.Zs")),
                        ]
                else:
                    for ni in n:
                        St.Pos[idx, :, ni] = (
                            St.Pos[idx - 1, :, ni] + St.V[idx - 1, :, ni] * dT
                        )

            if m > Tr.N:
                break

        # Обновляем высоту во вспомогательной переменной для evs-вызовов
        state.H = float(Tr.Pos[idx, 1])

        # Вектор скорости РЛС (Vx, Vh, Vz)
        Tr.V[idx, :] = [float(evs("Tr.Vx")), float(evs("Tr.Vy")), float(evs("Tr.Vz"))]

        # Углы ориентации осей ЛА
        Tr.Ang[idx, :] = np.deg2rad(
            [float(evs("Tr.tang")), float(evs("Tr.kren")), float(evs("Tr.psi"))]
        )

        if St.N > 0:
            for ni in n:
                St.V[idx, 0, ni] = float(evs("St.Vx"))  # вектор скорости Vx
                St.V[idx, 1, ni] = float(evs("St.Vy"))  # вектор скорости Vh
                St.V[idx, 2, ni] = float(evs("St.Vz"))  # вектор скорости Vz
                St.Ang[idx, 0, ni] = np.deg2rad(
                    float(evs("St.tang"))
                )  # углы ориентации осей целей
                St.Ang[idx, 1, ni] = np.deg2rad(
                    float(evs("St.kren"))
                )  # углы ориентации осей целей
                St.Ang[idx, 2, ni] = np.deg2rad(
                    float(evs("St.psi"))
                )  # углы ориентации осей целей

        # Обновляем параметры периода на первом шаге, начале пачки или ЛЧМ
        # Ym симметричная=3, несимметричная=1, симм. без расчёта обр.хода=?
        if (
            (m == 1)
            or (Ni > 0 and (m - 1) % Ni == 0)
            or (state.Ym > 0 and ((m - 1) % 2 == 0 or state.Ym < 3))
        ):
            Tr.Tm[idx] = float(
                evs("Rs.Tm")
            )  # период модуляции/повторения импульсов зонд.сигнала
            Tr.Tm_Ni[idx] = float(
                evs("Rs.Nimp")
            )  # число полупериодов в периоде (импульсов в пачке)
            Tr.Pz[idx] = float(evs("Rs.Pz"))  # мощность передатчика, Вт
            Ni = int(Tr.Tm_Ni[idx])  # продублируем во вспомогательной переменной
            if state.Ym == 0:
                Tr.Ti[idx] = float(
                    evs("Rs.tauimp")
                )  # длительность зондирующего импульса
        else:
            # Внутри пачки или периода СЛЧМ-модуляции — Tm,Tm_N,Ti не меняем
            Tr.Tm[idx] = Tr.Tm[idx - 1]  # период модуляции/повторения импульсов

        # Номер текущего полупериода в периоде (импульса в пачке)
        Tr.Tm_i[idx] = (m - 1) % max(Ni, 1) + 1

        # Обновляем время
        t = t + Tr.Tm[idx]
        if Ni > 0 and Tr.Tm_i[idx] == Ni:
            # Учтём доп. длительность паузы между периодами модуляции (между пачками)
            t = t + float(Rs.Tm_Pause)

    # Фактическая длина траектории (если была отмена — меньше исходной)
    if state.test.canceling == 1:
        Tr.N = max(int(Tr.t[Tr.t > 0].shape[0]) - 1, 1)
        Nimp = Tr.N  # noqa: F841

    # Диапазон точек для отображения (не более 11 если точек много)
    if Tr.N > 200:
        m_idx = np.round(np.linspace(0, Tr.N - 1, 11)).astype(int)
    else:
        m_idx = np.arange(Tr.N)

    # ==== Расчёт диапазона перемещений ====
    Tr.Lx = [float(np.min(Tr.Pos[m_idx, 0])), float(np.max(Tr.Pos[m_idx, 0]))]
    Tr.Lz = [float(np.min(Tr.Pos[m_idx, 2])), float(np.max(Tr.Pos[m_idx, 2]))]
    Tr.Lh = [float(np.min(Tr.Pos[m_idx, 1])), float(np.max(Tr.Pos[m_idx, 1]))]

    # Максимальная высота — обновляем H
    state.H = float(np.max(Tr.Pos[: Tr.N, 1]))

    # ==== Построение 3D-графика траектории ====
    fig = plt.figure(figsize=(6, 6), dpi=100)
    ax = fig.add_subplot(111, projection="3d")

    legend_labels = ["Локатор"]
    ax.plot(Tr.Pos[m_idx, 0], Tr.Pos[m_idx, 2], Tr.Pos[m_idx, 1], "-xm")

    if St.N > 0:
        for Cnt in n:
            legend_labels.append(f"Цель №{Cnt + 1}")
            ax.plot(
                St.Pos[m_idx, 0, Cnt],
                St.Pos[m_idx, 2, Cnt],
                St.Pos[m_idx, 1, Cnt],
                "-dr",
            )

    if St.N > 1:
        ax.set_title(
            "Траектории движения локатора+целей", fontsize=9, fontweight="normal"
        )
    elif St.N == 1:
        ax.set_title(
            "Траектории движения локатора+цели", fontsize=9, fontweight="normal"
        )
    else:
        ax.set_title("Траектория движения локатора", fontsize=9, fontweight="normal")

    ax.legend(legend_labels, loc="upper right")
    ax.set_xlabel("x (м)", fontsize=9)
    ax.set_ylabel("z (м)", fontsize=9)
    ax.set_zlabel("y (м)", fontsize=9)
    ax.grid(True)
    try:
        ax.set_box_aspect([1, 1, 1])
    except Exception:
        pass

    plt.tight_layout()
    save_fig_as_bmp("resultFig2.bmp")
