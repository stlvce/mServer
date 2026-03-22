from scripts import process_fm_radar, plot_fm_radar_results, save_fm_radar_results
import numpy as np


def test_do_sint_fm():
    globals = {
        "dtau": 1e-6,
        "c": 3e8,
        "Wd": 1e6,
        "H": 1.0,
        "ChannelN": 3,
        "Nimp": 64,
        "Timp": 1e-2,
        "SigCN": np.random.rand(3, 100, 100),
        "SigSN": np.random.rand(3, 100, 100),
        "Rs": {"Rmin": 0.0, "Rmax": 1000, "Log": True, "GB": 20},
    }

    RLIFM = process_fm_radar(globals)
    plot_fm_radar_results(globals)
    save_fm_radar_results(globals)
