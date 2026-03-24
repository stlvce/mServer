import numpy as np
from .do_sint_scan import (
    init_radar_image_processor_globals,
    process_radar_image,
    plot_radar_image_results,
    save_radar_image_results,
)

ChannelN = 32
globals = {
    "dtau": 1e-6,
    "c": 3e8,
    "H": 1.0,
    "ChannelN": ChannelN,
    "AnglZ_Prm": np.linspace(-30, 30, ChannelN),
    "ScosNN": np.random.rand(ChannelN, 1000),
    "SsinNN": np.random.rand(ChannelN, 1000),
    "Rs": {"Rmin": 0.0, "Rmax": 1000, "Log": True, "GB": 20},
    "test": {"canceling": 0},
}

init_radar_image_processor_globals(globals)
process_radar_image(globals)
plot_radar_image_results(globals)
save_radar_image_results(globals, "RLIscan.npz")
