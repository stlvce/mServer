from typing import List


# 1:1 = [1] / 1:2 = [1, 2] / .* поэлементное умнож / в функции подставляется тольк один элемент
def parse_colon(a: str) -> List[int]:
    param = a.split("=")
    param_range = param[1].split(":")
    arr_range = list(range(int(param_range[0]), int(param_range[1]) + 1))
    return f"{param[0]}={arr_range}"
