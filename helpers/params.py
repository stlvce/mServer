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
      't=(0)'
      'St.N=1'
      "Tr.Xa='0'"
      "St.Xs='evs(Tr.Xa)+10'"
      'H=evs(Tr.Ya)'
    """
    for var in vars_list:
        print(var)
        var = var.strip()
        if not var:
            continue

        key, _, raw_value = var.partition("=")
        key = _normalize_key(key.strip())
        raw_value = raw_value.strip()

        # Убираем внешние кавычки: 'evs(Tr.Xa)+10' -> evs(Tr.Xa)+10
        if (raw_value.startswith("'") and raw_value.endswith("'")) or (
            raw_value.startswith('"') and raw_value.endswith('"')
        ):
            raw_value = raw_value[1:-1]

        value = _evaluate(raw_value)
        _set_value(key, value)


# ---------------------------------------------------------------------------
# Внутренние функции
# ---------------------------------------------------------------------------


def _normalize_key(key: str) -> str:
    """Убирает лишние скобки из имени переменной: t=(0) -> t"""
    key = re.sub(r"[(){}\[\]]", "", key)
    return key.strip()


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
        setattr(_state, key, value)
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
