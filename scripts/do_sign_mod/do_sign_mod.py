import io
import numpy as np
import scipy.io
import matplotlib.pyplot as plt
from PIL import Image
import platform

from state import state
from .do_sign_imp import do_sign_imp
from .do_sign_fm import do_sign_fm


def _copy_to_clipboard(image: Image.Image):
    """Копирует PIL Image в буфер обмена (только Windows)."""
    if platform.system() != "Windows":
        return
    import win32clipboard
    from io import BytesIO

    output = BytesIO()
    image.convert("RGB").save(output, "BMP")
    data = output.getvalue()[14:]  # убрать BMP-заголовок
    output.close()
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
    win32clipboard.CloseClipboard()


def _save_fig_to_clipboard():
    """Сохраняет текущий график matplotlib в буфер обмена."""
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=100)
    plt.close()
    buf.seek(0)
    image = Image.open(buf)
    _copy_to_clipboard(image)
    buf.close()


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
                scipy.io.savemat("DataImp.mat", {"ScosNN": ScosNN, "SsinNN": SsinNN})
                print("Сохранение данных импульсного сигнала... DataImp.mat")

                # Огибающая отражённого сигнала
                envelope = np.abs(ScosNN[0] + 1j * SsinNN[0])
                plt.figure(figsize=(10, 5))
                plt.plot(envelope, color="blue")
                plt.title("Огибающая отражённого сигнала")
                plt.xlabel("Относительная дальность (м)")
                plt.ylabel("Амплитуда (норм.)")
                plt.grid(True)
                plt.tight_layout()
                # ==== Копируем график в буфер обмена ====
                _save_fig_to_clipboard()
                print(
                    "✅ График скопирован в буфер обмена (Windows). Можно вставить Ctrl+V."
                )

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
                # ==== Копируем график в буфер обмена ====
                _save_fig_to_clipboard()
                print(
                    "✅ ЛЧМ сигнал скопирован в буфер обмена (Windows). Можно вставить Ctrl+V."
                )

    # ==== Обработка исключений ====
    except Exception as e:
        print("❌ Ошибка при выполнении модели:")
        raise
