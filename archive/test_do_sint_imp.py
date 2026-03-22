import numpy as np
from scripts import (
    process_radar_impulse,
    plot_radar_impulse_results,
    init_radar_impulse_processor_globals,
    save_radar_impulse_results,
)


def test_do_sint_imp():
    globals = {
        "dtau": 1e-6,
        "c": 3e8,
        "H": 1.0,
        "ChannelN": 3,
        "Nimp": 64,
        "tauimp": 1e-3,
        "Sqw": 10,
        "Timp": 1e-2,
        "ScosNN": np.random.rand(3, 10000),  # 3 канала × 10000 отсчетов
        "SsinNN": np.random.rand(3, 10000),
        "Rs": {"Rmin": 0.0, "Rmax": 1000, "Log": True, "GB": 20, "Wnd": 1},
        "test": {"canceling": False, "h": {}, "fstep": [100, 100]},
    }

    init_radar_impulse_processor_globals(globals)
    process_radar_impulse(globals)
    plot_radar_impulse_results(globals)
    save_radar_impulse_results(globals, "RLIimp.npz")
