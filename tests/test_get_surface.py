import numpy as np
from scripts import calc_surface


def test_get_surface():
    calc_surface(
        50,
        {
            "Pos": np.array([[0, 100, 0], [100, 120, 50], [200, 150, 100]]),
            "Ang": np.zeros((3, 3)),
            "N": 3,
        },
        {
            "Pos": np.zeros((3, 3, 1)),
            "N": 1,
        },
        {
            "Kr": [1, 1, 1, 1, 1, 1, 1, 1],
            "DOR": [10] * 8,
            "dH": 1,
            "Type": 4,  # Лес
            "test": {"Nadir": 0},
            "Ncr": 0,
        },
    )
