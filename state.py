import numpy as np
from settings.models import Rs, Mi, Tr, St, test, Sf, Sea


class AppState:
    def __init__(self):
        # --- Вложенные объекты ---
        self.Rs = Rs()
        self.Mi = Mi()
        self.Tr = Tr()
        self.St = St()
        self.test = test()
        self.Sf = Sf()
        self.Sea = Sea()

        # --- Физические константы (не меняются от клиента) ---
        self.c: float = 3e8
        self.pi: float = 3.14
        self.g: float = 9.80665
        self.delta: float = 1e-6
        self.Wd: float = 1e6
        self.Pi2: float = self.pi * 2
        self.Pi4: float = self.pi * 4
        self.Pi4p3: float = self.Pi4**3
        self.mks: float = 1e-6
        self.ms: float = 1e-3
        self.ns: float = 1e-9
        self.X3: list = [1, 0, 0]
        self.Y3: list = [0, 1, 0]
        self.Z3: list = [0, 0, 1]
        self.X2: list = [1, 0]
        self.Y2: list = [0, 1]
        self.interpF: int = 1
        self.Grid: float = 0.02

        # --- Переменные состояния (приходят от клиента) ---
        self.t: int = 0
        self.H: float = 1.0
        self.Step: int = 0
        self.Type: int = 0
        self.FacetN: int = 0
        self.Ncr: int = 0
        self.vidDNA: str = "SC1"
        self.vidDOR1: str = "G"
        self.vidDOR2: str = "G"
        self.vidDOR7: str = "1"

        # --- Индексные переменные ---
        self.Ym: int = 0
        self.n: list = []
        self.nr: list = []
        self.ChannelN: int = 0
        self.DNA1n: int = 0
        self.DNA2n: int = 0
        self.f0n: float = 0.0
        self.AnglX_Prmn: int = 0
        self.AnglZ_Prmn: int = 0
        self.AnglX_Prdn: int = 0
        self.AnglZ_Prdn: int = 0
        self.Sqw: int = 0
        self.dH1: int = 0
        self.Kr1: int = 0
        self.DOR1: int = 0
        self.DOR2: int = 0
        self.dH2: int = 0
        self.Kr2: int = 0
        self.DOR7: int = 0
        self.dH7: int = 0
        self.Kr7: int = 0
        self.DOR8: int = 0
        self.dH8: int = 0
        self.Kr8: int = 0

        # --- Сигналы ---
        self.SigCN: np.ndarray = np.random.rand(3, 100, 100)
        self.SigSN: np.ndarray = np.random.rand(3, 100, 100)

        # --- Прочее ---
        self.Mark: set = {"kx", "bo", "g+", "md", "c^", "yo", "ms", "g*", "vr"}


# Глобальный синглтон — импортируется везде
state = AppState()


def evs(source: str):
    """
    Замена глобальной evs() из init_variables.py.
    Вычисляет выражение в контексте state.
    Пример: evs('Tr.Xa') -> state.Tr.Xa
            evs('Tr.Xa + 10') -> state.Tr.Xa + 10
    """
    import re

    def replace_attr(match):
        path = match.group(0)  # например 'Tr.Xa'
        parts = path.split(".")
        if len(parts) == 2:
            obj = getattr(state, parts[0], None)
            if obj is not None:
                val = getattr(obj, parts[1], None)
                if val is not None:
                    return str(val)
        return getattr(state, path, path)

    # Заменяем все 'Obj.attr' на их значения
    resolved = re.sub(r"[A-Z][a-zA-Z]*\.[a-zA-Z]+", replace_attr, source)

    try:
        return eval(resolved)
    except Exception:
        return resolved
