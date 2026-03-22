from state import state


def set_rv_param():
    """
    Установка общих параметров РВС/РЛС.
    Допустимы "избыточные" параметры для расширения возможностей.
    Внимание: время в с, частоты в Гц!
    """

    # Очистим траекторию для корректного старта с обновлёнными параметрами
    import numpy as np

    state.Tr.Pos = np.zeros((1, 3))
    state.Tr.Ang = None

    # Средняя длина волны (пропускаем если f0n не задан)
    if state.f0n != 0:
        state.Rs.Lambda = state.c / state.f0n

    # Позиции приёмных ФЦ АС РЛС, для графиков
    state.Rs.rx = [1, -1, 0, 0]  # по оси x (было Rs.x)
    state.Rs.rz = [0, 0, 1, -1]  # по оси z (было Rs.z)
    # Делим на 5 как в оригинале
    state.Rs.rx = [v / 5 for v in state.Rs.rx]
    state.Rs.rz = [v / 5 for v in state.Rs.rz]

    # Доп. спец параметры зондирующего сигнала и СВЧ тракта
    if state.Ym > 0:
        # Все 'FMCW'
        # Set_FmRvParam — расширение для ЛЧМ (пока не реализовано)
        pass
    else:
        # Все 'PULSE'
        # Set_ImRvParam — расширение для импульсного (пока не реализовано)
        pass
