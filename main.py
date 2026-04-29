import socket
import time

from helpers.format_error import format_error
from helpers.params import apply_params, init_params
from helpers.parse_msg import parse_msg
from scripts import do_sign_mod, do_step, get_mixyz, get_surface, get_traekt, show_dna
from settings.server import ans, rSrv
from state import state


def server_run():
    init_params(state)  # Связываем apply_params с глобальным state

    # Инициализация сервера
    rSrv.tStart = time.time()
    rSrv.server_info = socket.getaddrinfo(
        "localhost", rSrv.serverRecvPort, socket.AF_UNSPEC, socket.SOCK_DGRAM
    )
    rSrv.u = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    rSrv.u.bind((rSrv.serverIp, rSrv.serverRecvPort))
    rSrv.u.settimeout(1.0)
    rSrv.send(f"Hello from python mServer {ans}")

    try:
        while rSrv.cmd != "exit":
            try:
                # Получение сообщения от клиента
                data = rSrv.u.recvfrom(4096)
                rSrv.cmd = data[0].decode()
                rSrv.from_address = data[1]
                rSrv.log()

                # Получение параметров и команд с сообщения
                vars_list, commands = parse_msg(rSrv.cmd)

                # Выключение Python сервера
                if "exit" in commands:
                    break

                # Вывод ans версии
                if "ans" in commands:
                    ans_str = str(ans)
                    if len(ans_str) > 8000:
                        ans_str = ans_str[:8000] + " ..."
                    rSrv.send(f"Ok. ans={ans_str}")
                    continue

                # Отправка времени работы сервера
                if "server time" in commands:
                    rSrv.send(
                        f"Ok. Server uptime - {round(time.time() - rSrv.tStart)} s"
                    )
                    continue

                # Применяем параметры через безопасный apply_params
                apply_params(vars_list)

                # Шаг: РЛС-МИ
                if "Get_MiXyZ" in commands:
                    get_mixyz()
                    rSrv.send("Ok. Get_MiXyZ called")

                if "Show_DNA" in commands:
                    show_dna()
                    rSrv.send("Ok. Show_DNA called")

                # Шаг: Траект. Цель
                if "Get_Traekt" in commands:
                    get_traekt()
                    rSrv.send("Ok. Get_Traekt called")

                # Шаг: Фон
                if "Get_Surface" in commands:
                    state.cMass = get_surface()
                    rSrv.send("Ok. Get_Surface called")

                # Шаг: Предрасчет
                if "Do_SignMod" in commands:
                    do_sign_mod()
                    rSrv.send("Ok. Do_SignMod called")

                # Шаг: ПНМ
                if "Do_Step" in commands:
                    do_step()
                    rSrv.send("Ok. Do_Step called")

            # Ждём следующей итерации
            except socket.timeout:
                continue

            # Обработка ошибок
            except Exception as e:
                rSrv.lastErr = format_error(e)
                print(f"\n{rSrv.lastErr}")
                rSrv.send(rSrv.lastErr)

    # Обработка остановки сервера при Ctrl+C
    except KeyboardInterrupt:
        print("\n[INFO] Server stopped manually via Ctrl+C")

    # Отключение сервера при KeyboardInterrupt и команды "exit"
    finally:
        rSrv.send("Ok. UDP server is down")
        rSrv.u.close()


# Запуск сервера
if __name__ == "__main__":
    server_run()
