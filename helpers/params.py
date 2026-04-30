import dataclasses
import re
from typing import List

from state import APP_STATE_TYPES, state


def apply_params(vars_list: List[str]) -> None:
    """
    Разбирает список строк из UDP-сообщения и записывает значения
    в глобальный синглтон state.

    Поддерживаемые форматы:
        't=(0)'                  -> state.t = 0
        'St.N=1'                 -> state.St.N = 1
        "Tr.Xa='0'"              -> state.Tr.Xa = 0
        "St.Xs='evs(Tr.Xa)+10'" -> state.St.Xs = state.Tr.Xa + 10
        'H=evs(Tr.Ya)'          -> state.H = state.Tr.Ya
        'n=1:4'                  -> state.n = [1, 2, 3, 4]
        'vidDOR{1}=G'            -> state.vidDOR1 = 'G'
        'AnglZ_Prd(n)=0'         -> state.AnglZ_Prd[state.n - 1] = 0
        'Mi.a(3)=1'              -> state.Mi.a[2] = 1
    """
    for raw in vars_list:
        raw = raw.strip()
        if not raw:
            continue

        print(raw)

        key, _, val_str = raw.partition("=")
        key = key.strip()
        val_str = val_str.strip()

        # Снимаем внешние кавычки
        if len(val_str) >= 2 and val_str[0] in ("'", '"') and val_str[0] == val_str[-1]:
            val_str = val_str[1:-1]

        # Диапазон MATLAB-стиля: '1:4' -> [1, 2, 3, 4]
        if re.fullmatch(r"-?\d+:-?\d+", val_str):
            a, b = val_str.split(":")
            _write(key, list(range(int(a), int(b) + 1)))
            continue

        # Cell-array: vidDOR{1}=G -> state.vidDOR1 = 'G'
        m = re.fullmatch(r"(\w+)\{(\w+)}", key)
        if m:
            _write(f"{m.group(1)}{m.group(2)}", _eval(val_str))
            continue

        # Индексированное присваивание: Mi.a(3)=1  или  AnglZ_Prd(n)=0
        m = re.fullmatch(r"([\w.]+)\((\w+)\)", key)
        if m:
            _write_indexed(m.group(1), m.group(2), _eval(val_str))
            continue

        # Обычное присваивание, убираем лишние скобки из имени: t=(0) -> key='t'
        _write(re.sub(r"[(){}\[\]]", "", key).strip(), _eval(val_str))


# ---------------------------------------------------------------------------
# Запись в state
# ---------------------------------------------------------------------------


def _write(key: str, value) -> None:
    """Записывает скалярное значение в state по ключу 'Obj.attr' или 'attr'."""
    parts = key.split(".", 1)

    if len(parts) == 2:
        obj_name, attr = parts
        obj = getattr(state, obj_name, None)
        if obj is None:
            print(f"[WARN] params: неизвестный объект state.{obj_name}")
            return
        setattr(obj, attr, _coerce(obj, attr, value))

    else:
        typ = APP_STATE_TYPES.get(key)
        setattr(state, key, _cast(value, typ) if typ else value)


def _write_indexed(key: str, idx_str: str, value) -> None:
    """Записывает значение в элемент массива state по MATLAB-индексу (с 1)."""
    # Вычисляем индекс
    if idx_str.lstrip("-").isdigit():
        idx = int(idx_str) - 1
    else:
        raw = _read(idx_str)
        if raw is None:
            print(f"[WARN] params: индексная переменная '{idx_str}' не найдена")
            return
        idx = int(raw[0] if isinstance(raw, list) else raw) - 1

    # Получаем массив и модифицируем
    parts = key.split(".", 1)
    if len(parts) == 2:
        obj = getattr(state, parts[0], None)
        if obj is None:
            print(f"[WARN] params: неизвестный объект state.{parts[0]}")
            return
        arr = getattr(obj, parts[1], None)
        if arr is None:
            print(f"[WARN] params: поле {key} не найдено")
            return
        arr = _ensure_size(arr, idx, key)
        arr[idx] = value
        setattr(obj, parts[1], arr)
    else:
        arr = getattr(state, key, None)
        if arr is None:
            print(f"[WARN] params: переменная state.{key} не найдена")
            return
        arr = _ensure_size(arr, idx, key)
        arr[idx] = value
        setattr(state, key, arr)


# ---------------------------------------------------------------------------
# Вспомогательные функции для массивов
# ---------------------------------------------------------------------------


def _ensure_size(arr, idx: int, key: str):
    """
    Гарантирует, что arr содержит не менее idx+1 элементов.
    Список расширяется нулями, numpy-массив — через np.resize.
    Возвращает (возможно новый) массив.
    """
    if idx < len(arr):
        return arr
    print(f"[INFO] params: расширяем {key} с {len(arr)} до {idx + 1} элементов")
    try:
        import numpy as np

        if isinstance(arr, np.ndarray):
            new_arr = np.zeros(idx + 1, dtype=arr.dtype)
            new_arr[: len(arr)] = arr
            return new_arr
    except ImportError:
        pass
    if isinstance(arr, list):
        arr = arr + [0] * (idx + 1 - len(arr))
    return arr


# ---------------------------------------------------------------------------
# Чтение из state
# ---------------------------------------------------------------------------


def _read(path: str):
    """Возвращает значение из state по пути 'Obj.attr' или 'attr'."""
    parts = path.strip().split(".", 1)
    if len(parts) == 2:
        obj = getattr(state, parts[0], None)
        return getattr(obj, parts[1], None) if obj else None
    return getattr(state, parts[0], None)


# ---------------------------------------------------------------------------
# Вычисление выражений
# ---------------------------------------------------------------------------


def _eval(expr: str):
    """
    Вычисляет строку-значение:
      '100'         -> 100 (int)
      '3.14'        -> 3.14 (float)
      'evs(Tr.Xa)'  -> state.Tr.Xa
      'tauimp/2'    -> вычисляется в контексте переменных state
      'текст'       -> str
    """
    # evs(...) — получение значения из state
    if "evs(" in expr:
        resolved = re.sub(
            r"evs\(([^)]+)\)",
            lambda m: str(_read(m.group(1)) or 0),
            expr,
        )
        try:
            return eval(resolved, {"__builtins__": {}}, _state_ctx())
        except Exception:
            return resolved

    # Попытка распарсить как число
    clean = expr.strip().strip("()")
    for cast in (int, float):
        try:
            return cast(clean)
        except (ValueError, TypeError):
            pass

    # Попытка вычислить как математическое выражение через переменные state
    ctx = _state_ctx()
    try:
        return eval(clean, {"__builtins__": {}}, ctx)
    except Exception:
        return clean  # оставляем строкой


def _state_ctx() -> dict:
    """Строит словарь числовых переменных state для eval."""
    ctx: dict = {}
    for k, v in vars(state).items():
        if isinstance(v, (int, float)):
            ctx[k] = v
    for obj in vars(state).values():
        if dataclasses.is_dataclass(obj):
            for f in dataclasses.fields(obj):
                v = getattr(obj, f.name, None)
                if isinstance(v, (int, float)):
                    ctx.setdefault(f.name, v)
    return ctx


# ---------------------------------------------------------------------------
# Приведение типов
# ---------------------------------------------------------------------------


def _coerce(obj, attr: str, value):
    """Приводит value к типу поля dataclass-объекта."""
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
