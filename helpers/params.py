import re
import dataclasses
from typing import List

# Инициализируется один раз через init_params(state)
_state = None


def init_params(state):
    """Вызвать один раз при старте сервера: init_params(state)"""
    global _state
    _state = state


def apply_params(vars_list: List[str]):
    """
    Парсит и применяет список строк вида:
      't=(0)'             -> state.t = 0
      'St.N=1'            -> state.St.N = 1
      "Tr.Xa='0'"         -> state.Tr.Xa = 0
      "St.Xs='evs(Tr.Xa)+10'" -> state.St.Xs = Tr.Xa + 10
      'H=evs(Tr.Ya)'      -> state.H = Tr.Ya
      'n=1:4'             -> state.n = [1, 2, 3, 4]
      'vidDOR{1}=G'       -> state.vidDOR1 = 'G'    (cell array -> имя+индекс)
      'AnglZ_Prd(n)=0'    -> state.AnglZ_Prd[n-1] = 0  (массив по индексу)
      'Mi.a(3)=1'         -> state.Mi.a[2] = 1          (массив по индексу, -1 для MATLAB->Python)
    """
    for var in vars_list:
        var = var.strip()
        if not var:
            continue

        key, _, raw_value = var.partition("=")
        key = key.strip()
        raw_value = raw_value.strip()

        # Убираем внешние кавычки: 'evs(Tr.Xa)+10' -> evs(Tr.Xa)+10
        if (raw_value.startswith("'") and raw_value.endswith("'")) or (
            raw_value.startswith('"') and raw_value.endswith('"')
        ):
            raw_value = raw_value[1:-1]

        # Обработка диапазона через двоеточие: '1:4' -> [1, 2, 3, 4]
        if re.match(r"^-?\d+:-?\d+$", raw_value):
            _set_value(_normalize_key(key), _parse_colon(raw_value))
            continue

        # Обработка cell array: vidDOR{1} -> vidDOR1
        # В MATLAB {} это cell array, здесь храним как отдельные переменные с суффиксом
        cell_match = re.match(r"^(\w+)\{(\w+)}$", key)
        if cell_match:
            name, idx = cell_match.groups()
            flat_key = f"{name}{idx}"  # vidDOR{1} -> vidDOR1
            _set_value(flat_key, _evaluate(raw_value))
            continue

        # Обработка индексированного присваивания: AnglZ_Prd(n)=0 или Mi.a(3)=1
        # Формат: имя(индекс) или Obj.поле(индекс)
        indexed_match = re.match(r"^([\w.]+)\((\w+)\)$", key)
        if indexed_match:
            base_key, idx_str = indexed_match.groups()
            _set_indexed(base_key, idx_str, _evaluate(raw_value))
            continue

        # Обычное присваивание
        _set_value(_normalize_key(key), _evaluate(raw_value))


# ---------------------------------------------------------------------------
# Внутренние функции
# ---------------------------------------------------------------------------


def _parse_colon(value: str) -> list:
    """
    Разворачивает диапазон MATLAB-стиля в список.
    '1:4'   -> [1, 2, 3, 4]
    '1:1'   -> [1]
    '-2:2'  -> [-2, -1, 0, 1, 2]
    """
    start, end = value.split(":")
    return list(range(int(start), int(end) + 1))


def _normalize_key(key: str) -> str:
    """
    Убирает скобки из имени переменной.
      't=(0)' -> 't'   (скобки вокруг значения, не индекс)
      't'     -> 't'
    Не трогает индексированные выражения — они обрабатываются отдельно.
    """
    # Убираем голые скобки без содержимого смысла: t=(0) -> key уже просто 't'
    key = re.sub(r"[(){}\[\]]", "", key)
    return key.strip()


def _set_indexed(base_key: str, idx_str: str, value):
    """
    Присваивает значение элементу массива по индексу.
    MATLAB индексы начинаются с 1, Python — с 0, поэтому idx-1.

    Если idx_str — переменная (например 'n'), берём её значение из state.
    Если idx_str — число, конвертируем напрямую.

    Примеры:
      'AnglZ_Prd', 'n', 0  -> state.AnglZ_Prd[state.n - 1] = 0
      'Mi.a',      '3', 1  -> state.Mi.a[2] = 1
    """
    # Определяем индекс
    if idx_str.lstrip("-").isdigit():
        idx = int(idx_str) - 1  # MATLAB -> Python (с 1 на 0)
    else:
        # Индекс — переменная из state, например n
        idx_val = _get_from_state(idx_str)
        if idx_val is None:
            print(f"[WARN] Индексная переменная '{idx_str}' не найдена в state")
            return
        # Если переменная — список (результат n=1:1), берём первый элемент
        if isinstance(idx_val, list):
            idx_val = idx_val[0]
        idx = int(idx_val) - 1  # MATLAB -> Python

    # Получаем массив из state
    parts = base_key.split(".")
    if len(parts) == 2:
        obj = getattr(_state, parts[0], None)
        if obj is None:
            print(f"[WARN] Неизвестный объект: {parts[0]}")
            return
        arr = getattr(obj, parts[1], None)
        if arr is None:
            print(f"[WARN] Поле {base_key} не найдено")
            return
        arr[idx] = value
        setattr(obj, parts[1], arr)
    elif len(parts) == 1:
        arr = getattr(_state, base_key, None)
        if arr is None:
            print(f"[WARN] Переменная {base_key} не найдена в state")
            return
        arr[idx] = value
        setattr(_state, base_key, arr)


def _evaluate(expr: str):
    """
    Вычисляет строку-выражение.
      evs(Tr.Xa)    -> значение state.Tr.Xa
      evs(Tr.Xa)+10 -> float(state.Tr.Xa) + 10
      '100'         -> int 100
      '3.14'        -> float 3.14
    """
    if "evs(" not in expr:
        return _parse_scalar(expr)

    def replace_evs(match):
        inner = match.group(1)  # например "Tr.Xa"
        val = _get_from_state(inner)
        return str(val) if val is not None else "0"

    resolved = re.sub(r"evs\(([^)]+)\)", replace_evs, expr)

    try:
        from state import evs  # noqa — доступна в eval если вдруг осталась

        return eval(resolved, {"evs": evs})
    except Exception:
        return resolved


def _get_from_state(path: str):
    """Получает значение из state по пути 'Tr.Xa' или 'H'."""
    if _state is None:
        return None
    parts = path.strip().split(".")
    if len(parts) == 2:
        obj = getattr(_state, parts[0], None)
        return getattr(obj, parts[1], None) if obj else None
    elif len(parts) == 1:
        return getattr(_state, parts[0], None)
    return None


def _set_value(key: str, value):
    """Устанавливает значение в state: 'St.N' или 'H'."""
    if _state is None:
        print("[WARN] state не инициализирован, вызовите init_params(state)")
        return

    parts = key.split(".")
    if len(parts) == 2:
        obj_name, attr = parts
        obj = getattr(_state, obj_name, None)
        if obj is None:
            print(f"[WARN] Неизвестный объект: {obj_name}")
            return
        setattr(obj, attr, _cast_by_field(obj, attr, value))
    elif len(parts) == 1:
        # Используем APP_STATE_TYPES для приведения типов верхнего уровня
        from state import APP_STATE_TYPES

        typ = APP_STATE_TYPES.get(key)
        typed_value = _cast(value, typ) if typ else value
        setattr(_state, key, typed_value)
    else:
        print(f"[WARN] Не удалось применить ключ: {key}")


def _cast_by_field(obj, attr: str, value):
    """Приводит value к типу поля dataclass."""
    if not dataclasses.is_dataclass(obj):
        return value
    for f in dataclasses.fields(obj):
        if f.name == attr:
            return _cast(value, f.type)
    return value


def _cast(value, typ):
    try:
        if typ in (int, "int"):
            return int(float(str(value)))
        if typ in (float, "float"):
            return float(value)
        if typ in (str, "str"):
            return str(value)
        if typ in (bool, "bool"):
            return str(value).lower() == "true"
    except (ValueError, TypeError):
        pass
    return value


def _parse_scalar(value: str):
    """Автоопределение типа: int -> float -> str."""
    for typ in (int, float):
        try:
            return typ(value)
        except (ValueError, TypeError):
            pass
    return value
