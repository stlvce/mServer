from socket import socket, AF_INET, SOCK_DGRAM
from datetime import datetime

ans = "v.2.2"


class RSrv:
    def __init__(self):
        self.serverIp = ""
        self.serverSendPort = 9099
        self.serverRecvPort = 9098
        self.toIP = "localhost"
        self.toPort = 9092
        self.server_info: list[tuple] | None = None
        self.u: socket | None = None
        self.s: socket | None = None
        self.tStart = 0
        self.from_address = ""
        self.cmd = ""
        self.lastErr = ""
        self.tStart: float

        print(f"UDP server running with port {self.serverRecvPort}")

    def log(
        self,
    ):
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n{formatted_datetime}")
        print(f"Отправитель: {self.from_address}")
        print(f"Сообщение: {self.cmd}")

    def send(self, msg: str):
        # Создание сокета для отправки
        self.s = socket(AF_INET, SOCK_DGRAM)
        self.s.bind((self.serverIp, self.serverSendPort))

        # Подключение к клиентскому SamRLSim
        self.s.connect((self.toIP, self.toPort))

        # Отправка сообщения удаленному хосту
        self.s.sendto(msg.encode(), (self.toIP, self.toPort))

        self.s.close()


rSrv = RSrv()
