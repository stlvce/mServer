import io
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import platform
from scripts.do_sign_imp import do_sign_imp
from scripts.do_sign_fm import do_sign_fm

from state import state


def do_sign_mod():
    Ym = state.Ym

    try:
        if Ym == 0:
            print("Запуск модели для импульсного сигнала...")
            ScosNN, SsinNN = do_sign_imp()  # функция моделирования импульсного сигнала

            print("Сохранение данных импульсного сигнала...")

            # Огибающая отражённого сигнала
            envelope = np.abs(ScosNN + 1j * SsinNN)
            plt.figure(figsize=(10, 5))
            plt.plot(envelope, color="blue")
            plt.title("Огибающая отражённого сигнала")
            plt.xlabel("Относительная дальность (м)")
            plt.ylabel("Амплитуда (норм.)")
            plt.grid(True)
            plt.tight_layout()

            # ==== сохраняем график в память ====
            buf = io.BytesIO()
            plt.savefig(buf, format="png", dpi=100)
            plt.close()
            buf.seek(0)
            image = Image.open(buf)

            # ==== копируем график в буфер обмена ====
            sysname = platform.system()
            if sysname == "Windows":
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
                print(
                    "✅ График скопирован в буфер обмена (Windows). Можно вставить Ctrl+V."
                )

        else:
            print("Запуск модели для ЛЧМ сигнала...")
            SigSN = do_sign_fm()  # функция моделирования ЛЧМ сигнала
            print("Сохранение данных ЛЧМ сигнала...")
            plt.figure(figsize=(10, 5))
            plt.plot(SigSN, color="green")
            plt.title("ЛЧМ сигнал")
            plt.xlabel("Относительное время (отсчёты)")
            plt.ylabel("Амплитуда (норм.)")
            plt.grid(True)
            plt.tight_layout()

            buf = io.BytesIO()
            plt.savefig(buf, format="png", dpi=100)
            plt.close()
            buf.seek(0)
            image = Image.open(buf)
            sysname = platform.system()
            if sysname == "Windows":
                import win32clipboard
                from io import BytesIO

                output = BytesIO()
                image.convert("RGB").save(output, "BMP")
                data = output.getvalue()[14:]
                output.close()
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
                win32clipboard.CloseClipboard()
                print(
                    "✅ ЛЧМ сигнал скопирован в буфер обмена (Windows). Можно вставить Ctrl+V."
                )

    # ==== Обработка исключений ====
    except Exception as e:
        print("❌ Ошибка при выполнении модели:")
        print(e)
        raise
