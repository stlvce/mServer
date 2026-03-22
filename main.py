import socket
import time

from settings.server import rSrv, ans
from state import state
from helpers.params import apply_params, init_params
from scripts import get_traekt, get_mixyz, do_sign_mod, calc_surface, do_step


def _format_error(e: Exception) -> str:
    """
    Возвращает сообщение об ошибке с указанием файла и строки
    где исключение реально возникло (последний фрейм traceback).
    """
    import traceback

    tb = e.__traceback__
    if tb is None:
        return str(e)

    # Идём до последнего фрейма в цепочке
    while tb.tb_next is not None:
        tb = tb.tb_next

    filename = tb.tb_frame.f_code.co_filename
    lineno = tb.tb_lineno
    func = tb.tb_frame.f_code.co_name

    # Полный traceback для лога в консоль
    full_tb = "".join(traceback.format_exception(type(e), e, e.__traceback__))
    print(full_tb)

    return f"{str(e)} | In_file: {filename}, line {lineno}, in {func}"


def server_run():
    print(f"UDP server running with port {rSrv.serverRecvPort}")
    init_params(state)  # Связываем apply_params с глобальным state
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
                data = rSrv.u.recvfrom(4096)
                rSrv.cmd = data[0].decode()
                rSrv.from_address = data[1]
                rSrv.log()

                vars_list = []
                commands = []

                for i in rSrv.cmd.split("; "):
                    if i.strip() == "":
                        continue
                    if "=" in i:
                        vars_list.append(i)
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

                if "Get_MiXyZ" in commands:
                    get_mixyz(
                        Nmax=state.Mi.Nmax,
                        Rs=state.Mi.Rs,
                        Rz=state.Mi.Rz,
                        Ry=state.Mi.Ry,
                        Zmax=state.Mi.Zmax,
                        Ymax=state.Mi.Ymax,
                        figext=state.test.figext,
                        result_path="resultFig1.bmp",
                    )
                    rSrv.send("Ok. Get_MiXyZ called")

                # Шаг: Траект. Цель
                if "Get_Traekt" in commands:
                    get_traekt(
                        Nimp=int(state.Rs.Nimp),
                        Xa=int(state.Tr.Xa),
                        Ya=int(state.Tr.Ya),
                        Za=int(state.Tr.Za),
                        Vx=int(state.Tr.Vx),
                        Vy=int(state.Tr.Vy),
                        Vz=int(state.Tr.Vz),
                        St_N=int(state.St.N),
                        St_Xs=int(state.Tr.Xa) + 20,
                        St_Ys=int(state.Tr.Ya),
                        St_Zs=int(state.Tr.Za),
                    )
                    rSrv.send("Ok. Get_Traekt called")

                # Шаг: Фон
                if "Get_Surface" in commands:
                    cMass = calc_surface()
                    print(cMass)
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
                rSrv.lastErr = _format_error(e)
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
