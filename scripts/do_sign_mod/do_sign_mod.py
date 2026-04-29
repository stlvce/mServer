import matplotlib.pyplot as plt
import numpy as np
import scipy.io

from helpers import copy_fig_to_clipboard
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
                # ==== Сохраняем данные импульсного сигнала ====
                # scipy.io.savemat("DataImp.mat", {"ScosNN": ScosNN, "SsinNN": SsinNN})
                # print("Сохранение данных импульсного сигнала... DataImp.mat")

                # Огибающая отражённого сигнала
                envelope = np.abs(ScosNN[0] + 1j * SsinNN[0])
                plt.figure(figsize=(10, 5))
                plt.plot(envelope, color="blue")
                plt.title("Огибающая отражённого сигнала")
                plt.xlabel("Относительная дальность (м)")
                plt.ylabel("Амплитуда (норм.)")
                plt.grid(True)
                plt.tight_layout()

            else:
                # ==== Сохраняем данные ЛЧМ сигнала ====
                scipy.io.savemat(
                    "DataFM.mat", {"SigSN": SigSN, "SigCN": SigCN, "Ni": Ni}
                )
                print("Сохранение данных ЛЧМ сигнала... DataFM.mat")

                plt.figure(figsize=(10, 5))
                plt.plot(SigSN, color="green")
                plt.title("ЛЧМ сигнал")
                plt.xlabel("Относительное время (отсчёты)")
                plt.ylabel("Амплитуда (норм.)")
                plt.grid(True)
                plt.tight_layout()

            copy_fig_to_clipboard()

    # ==== Обработка исключений ====
    except Exception as e:
        print("❌ Ошибка при выполнении модели:")
        raise
