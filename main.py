import socket
import time

from settings.server import rSrv, ans
from settings.init_variables import *  # noqa: F403
from helpers import send_message, print_log, get_params
from scripts import get_traekt, get_mixyz, do_sign_mod, calc_surface


def server_run():
    print(f"UDP server running with port {rSrv.serverRecvPort}")
    rSrv.tStart = time.time()  # Время запуска программы
    rSrv.server_info = socket.getaddrinfo(
        "localhost", rSrv.serverRecvPort, socket.AF_UNSPEC, socket.SOCK_DGRAM
    )  # Информация о сервере
    rSrv.u = socket.socket(
        socket.AF_INET, socket.SOCK_DGRAM
    )  # Создание порта для получения сообщений
    rSrv.u.bind((rSrv.serverIp, rSrv.serverRecvPort))
    rSrv.u.settimeout(1.0)  # Устанавливаем таймаут в 1 секунду
    send_message(
        f"Hello from python mServer {ans}"
    )  # Отправка приветственного сообщения

    try:
        while rSrv.cmd != "exit":
            try:
                data = rSrv.u.recvfrom(4096)  # Ожидание запроса
                rSrv.cmd = data[0].decode()  # Получение сообщения из запроса
                print_log(
                    rSrv.cmd, data[1]
                )  # Вывод в логи сообщение, которое пришло с SamRLSim

                vars = []  # Параметры из запроса для выполнения команд
                commands = []  # Команды, которые необходимо выполнить

                for i in rSrv.cmd.split("; "):
                    if i.strip() == "":
                        continue

                    if "=" in i:
                        vars.append(i)
                    else:
                        commands.append(i)

                # Выключение Python сервера
                if "exit" in commands:
                    break

                # Вывод ans версии
                if "ans" in commands:
                    ans_str = str(ans)
                    if len(ans_str) > 8000:
                        ans_str = ans_str[:8000] + " ..."
                    send_message(f"Ok. ans={ans_str}")
                    continue

                # Отправка времени работы сервера
                if "server time" in commands:
                    send_message(
                        f"Ok. Server uptime - {round(time.time() - rSrv.tStart)} s"
                    )
                    continue

                # Установка констант
                # if "Set_Consts" in commands:
                #     send_message("Ok. Consts set")

                """
                Сохранения в глобальный контекст параметров и выполнение команд из запроса
                """

                # Выполняем присваивание
                parsed_params = get_params(vars)
                for el in parsed_params:
                    print("Параметр", el)
                    exec(el, globals())

                # Шаг: РЛС-МИ
                if "Get_MiXyZ" in commands:
                    get_mixyz(
                        Nmax=globals()["Mi"].Nmax,
                        Rs=globals()["Mi"].Rs,
                        Rz=globals()["Mi"].Rz,
                        Ry=globals()["Mi"].Ry,
                        Zmax=globals()["Mi"].Zmax,
                        Ymax=globals()["Mi"].Ymax,
                        figext=globals()["test"].figext,
                        result_path="resultFig1.bmp",
                    )

                    send_message("Ok. Get_MiXyZ called")

                # Шаг: Траект. Цель
                if "Get_Traekt" in commands:
                    get_traekt(
                        Nimp=int(globals()["Rs"].Nimp),
                        Xa=int(globals()["Tr"].Xa),
                        Ya=int(globals()["Tr"].Ya),
                        Za=int(globals()["Tr"].Za),
                        Vx=int(globals()["Tr"].Vx),
                        Vy=int(globals()["Tr"].Vy),
                        Vz=int(globals()["Tr"].Vz),
                        St_N=int(globals()["St"].N),
                        St_Xs=int(globals()["Tr"].Xa) + 20,
                        St_Ys=int(globals()["Tr"].Ya),
                        St_Zs=int(globals()["Tr"].Za),
                    )

                    send_message("Ok. Get_Traekt called")

                # Шаг: Фон
                if "Get_Surface" in commands:
                    cMass = calc_surface(globals())
                    print(cMass)

                    send_message("Ok. Get_Surface called")

                # Шаг: Предрасчет
                if "Do_SignMod" in commands:
                    do_sign_mod(globals())

                    send_message("Ok. Do_SignMod called")

                # Шаг: ПНМ
                if "Do_Step" in commands:
                    send_message("Ok. Do_Step called")

            # Ждём следующей итерации
            except socket.timeout:
                continue

            # Обработка ошибок
            except Exception as e:
                if e.__traceback__ is not None:
                    rSrv.lastErr = f"{str(e)} In_file: {e.__traceback__.tb_frame.f_code.co_filename}, line {e.__traceback__.tb_lineno}"
                else:
                    rSrv.lastErr = f"{str(e)}"
                print(f"\n{rSrv.lastErr}")
                send_message(rSrv.lastErr)

    # Обработка остановки сервера при Ctrl+C
    except KeyboardInterrupt:
        print("\n[INFO] Server stopped manually via Ctrl+C")

    # Отключение сервера при KeyboardInterrupt и команды "exit"
    finally:
        send_message("Ok. UDP server is down")
        rSrv.u.close()


# Запуск сервера
if __name__ == "__main__":
    server_run()
