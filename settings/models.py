from dataclasses import dataclass, field
import numpy as np


@dataclass
class Rs:
    Nimp: int = 256
    Polariz: str = "HH"
    Timp: float = 1e-2
    dtau: float = 1e-6
    tauimp: float = 10e-9
    AruType: int = 0
    sh: int = 0
    maxF: float = 0.0
    Hmax: int = 0
    Pz: str = "1"
    snr: str = "100"
    Tm_Pause: int = 0
    Rmin: int = 0
    Rmax: int = 0
    GB: int = 0
    Log: int = 0
    Wnd: int = 0
    Focus: int = 0
    Logi: int = 0


@dataclass
class Mi:
    Ry: int = 0
    Rz: int = 0
    Rs: int = 0
    a1: int = 0
    a2: int = 0
    a3: int = 0
    a4: int = 0
    y: int = 0
    z: int = 0
    Ymax: int = 0
    Zmax: int = 0
    Nmax: int = 0
    dnay: int = 0
    dnaz: int = 0


@dataclass
class Tr:
    Xa: float = 0.0
    Ya: float = 100.0
    Za: float = 0.0
    Vx: float = 100.0
    Vy: float = 0.0
    Vz: float = 0.0
    tang: float = 30.0
    kren: float = 0.0
    psi: float = 0.0
    Pos: np.ndarray = field(default_factory=lambda: np.array([]))
    Ang: object = None


@dataclass
class St:
    N: int = 0
    Vx: float = 0.0
    Vy: float = 0.0
    Vz: float = 0.0
    tang: float = 0.0
    kren: float = 0.0
    psi: float = 0.0
    Model: str = "0"
    Type: str = "1"
    wx: int = 0
    wh: int = 0
    wz: int = 0
    RSC: int = 0
    Xs: float = 0.0
    Ys: float = 0.0
    Zs: float = 0.0
    Pos: np.ndarray = field(default_factory=lambda: np.array([]))


@dataclass
class test:
    figext: int = 0
    Xcr: float = 0.0
    Zcr: float = 0.0
    Nadir: int = 0
    SWT: int = 0
    pF: int = 0
    pN: int = 0
    cycleN: int = 0
    n_figs: int = 7
    hn_figs: int = 0
    scrsz: int = 0
    cash_Enabled: int = 0
    mem_i: int = -1
    fpos: list = field(default_factory=lambda: [1, 1, 576, 512])
    fstep: list = field(default_factory=lambda: [100, 24])


@dataclass
class Sf:
    Relief: str = ""
    Kspot: float = 0.0
    KspotN: float = 0.0
    WindTh: int = 0
    WindFi: int = 0
    AirT: int = 0
    TownD: int = 0
    XZstep: int = 0
    maxY: int = 0
    Elev: int = 0
    Dspot: int = 0
    x: int = 0
    z: int = 0
    rad_mul: float = 0.0
    x_size: int = 0
    z_size: int = 0
    med_shift: float = 0.0
    n: int = 0
    Color: list = field(
        default_factory=lambda: [
            10,
            0.412,
            0.267,
            0.141,
            20,
            0.678,
            0.922,
            1.0,
            30,
            0.467,
            0.675,
            0.188,
            40,
            0.231,
            0.443,
            0.337,
            50,
            0.8,
            0.8,
            0.8,
            60,
            0.929,
            0.694,
            0.125,
            70,
            0.392,
            0.475,
            0.635,
            80,
            0.871,
            0.49,
            0.0,
        ]
    )
    Color_name: dict = field(
        default_factory=lambda: {
            10: "ground",
            20: "water",
            30: "meadow",
            40: "forest",
            50: "snow",
            60: "sand",
            70: "road",
            80: "bushes",
        }
    )


@dataclass
class Sea:
    rho: int = 0
    WindV: int = 0
    WaveL: int = 0
    Shift: int = 0
    depth: int = 0
    nr: int = 0
