import matplotlib.pyplot as plt
import numpy as np
import scipy.io

from helpers import copy_fig_to_clipboard
from settings.server import rSrv
from state import state

from .do_sign_fm import do_sign_fm
from .do_sign_imp import do_sign_imp


def do_sign_mod():
    """
    Расчёт сигнала отражённого от поверхности — выбор по типу сигнала.
    Ym==0 — импульсный сигнал (Do_SignImp)
    Ym>0  — ЛЧМ сигнал (Do_SignFM)
    """
    state.test.canceling = 0  # сброс флага отмены
    perc = 0  # процент выполнения

    try:
        if state.Ym == 0:
            print("Запуск модели для импульсного сигнала...")
            ScosNN, SsinNN = do_sign_imp()  # функция моделирования импульсного сигнала

        else:
            print("Запуск модели для ЛЧМ сигнала...")
            SigSN, SigCN, Ni = do_sign_fm()  # функция моделирования ЛЧМ сигнала

        # ==== Обработка результата после завершения ====
        if state.test.canceling:
            # Расчёт прерван по кнопке Cancel
            print(f"Запуск модели прерван по кнопке Cancel. Percent={perc}")
            # Отправка статуса отмены в SamRLSim (выполняется в server.py через send_message)
            state.test.cancel_message = f"Cancel. Percent={perc}"

        else:
            if state.Ym == 0:
                # Сохраняем данные импульсного сигнала (аналог: save DataImp.mat)
                scipy.io.savemat("DataImp.mat", {"ScosNN": ScosNN, "SsinNN": SsinNN})
                print("Сохранение данных импульсного сигнала... DataImp.mat")
                # Построение графика в MATLAB закомментировано — здесь тоже не строим

            else:
                # Сохраняем данные ЛЧМ сигнала (аналог: save DataFM.mat)
                scipy.io.savemat(
                    "DataFM.mat", {"SigSN": SigSN, "SigCN": SigCN, "Ni": Ni}
                )
                print("Сохранение данных ЛЧМ сигнала... DataFM.mat")

                # Аналог plot(SigSN): SigSN может быть 3D (каналы × антенны × отсчёты),
                # приводим к 2D — (отсчёты × N кривых) и строим все кривые первого канала
                sig_2d = SigSN[0].T  # (samples, antennas)
                plt.figure(figsize=(6, 3))
                plt.plot(sig_2d)
                plt.title("ЛЧМ сигнал")
                plt.xlabel("Относительная дальность (отсчёты)")
                plt.ylabel("Амплитуда (норм.)")
                plt.grid(True)
                plt.tight_layout()

            copy_fig_to_clipboard()

    # ==== Обработка исключений ====
    except Exception as e:
        print("❌ Ошибка при выполнении модели:")
        raise
