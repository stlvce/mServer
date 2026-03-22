import numpy as np
from settings.models import Rs, Mi, Tr, St, test, Sf, Sea


# Типы полей верхнего уровня AppState — используются в apply_params для кастинга
APP_STATE_TYPES: dict = {
    "t": int,
    "H": float,
    "Step": int,
    "Type": int,
    "FacetN": int,
    "Ncr": int,
    "Ym": int,
    "Sqw": int,
    "ChannelN": int,
    "DNA1n": int,
    "DNA2n": int,
    "f0n": float,
    "AnglX_Prmn": int,
    "AnglZ_Prmn": int,
    "AnglX_Prdn": int,
    "AnglZ_Prdn": int,
    "dH1": int,
    "Kr1": int,
    "DOR1": int,
    "dH2": int,
    "Kr2": int,
    "DOR2": int,
    "dH7": int,
    "Kr7": int,
    "DOR7": int,
    "dH8": int,
    "Kr8": int,
    "DOR8": int,
    "vidDNA": str,
    "vidDOR1": str,
    "vidDOR2": str,
    "vidDOR7": str,
}


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

    # Также заменяем одиночные переменные state верхнего уровня (ns, ms, c и т.д.)
    def replace_scalar(match):
        name = match.group(0)
        val = getattr(state, name, None)
        if val is not None and isinstance(val, (int, float)):
            return str(val)
        return name

    resolved = re.sub(r"\b([a-z_][a-zA-Z0-9_]*)\b", replace_scalar, resolved)

    # Контекст для eval: все числовые константы из state
    ctx = {k: v for k, v in vars(state).items() if isinstance(v, (int, float))}

    try:
        return eval(resolved, {"__builtins__": {}}, ctx)
    except Exception:
        return resolved
