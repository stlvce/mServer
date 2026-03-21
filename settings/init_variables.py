from typing import Literal, List
import numpy as np


def evs(source: str):
    eval(source)


c = 3e8
pi = 3.14
g = 9.80665
delta = 1e-6
Wd = 1e6
Pi2 = pi * 2
Pi4 = pi * 4
Pi4p3 = Pi4**3
mks = 1e-6
ms = 1e-3
ns = 1e-9
X3 = [1, 0, 0]
Y3 = [0, 1, 0]
Z3 = [0, 0, 1]
X2 = [1, 0]
Y2 = [0, 1]


Mark = {"kx", "bo", "g+", "md", "c^", "yo", "ms", "g*", "vr"}
interpF = 1
Grid = 0.02


ns = 10 ** (-9)
Ym: int
n: List[int]
nr: List[int]
ChannelN: int
DNA1n: int
DNA2n: int
f0n: float
AnglX_Prmn: int
AnglZ_Prmn: int
AnglX_Prdn: int
AnglZ_Prdn: int
Sqw: int
vidDNA = "SC1"
t: Literal[0] = 0
H = 1
# H = "evs(Tr.Ya)"
Type: int
FacetN: int
vidDOR1: str = "G"
dH1: int
Kr1: int
DOR1: int
DOR2: int
dH2: int
Kr2: int
vidDOR2: str = "G"
DOR7: int
dH7: int
Kr7: int
vidDOR7: str = "G"
Ncr: int
DOR8: int
dH8: int
Kr8: int
vidDOR7: str = "1"
Step: int


SigCN = np.random.rand(3, 100, 100)
SigSN = np.random.rand(3, 100, 100)


class Rs:
    Nimp: int = 256
    Polariz: str = "HH"
    # Timp = "tauimp*Sqw"
    Timp = 1e-2
    dtau = 1e-6
    # dtau = "tauimp/2"
    tauimp = "10*ns"
    AruType: int
    sh: int
    maxF: float
    Hmax: int
    Pz: str = "1"
    snr: str = "100"
    Tm_Pause: int
    Rmin: int
    Rmax: int
    GB: int
    Log: int
    Wnd: int
    Focus: int
    Logi: int
    Rmin: int
    Rmax: int
    GB: int
    Log: int
    Wnd: int
    Focus: int


class Mi:
    Ry: int
    Rz: int
    Rs: int
    a1: int
    a2: int
    a3: int
    a4: int
    y: int
    z: int
    Ymax: int
    Zmax: int
    Nmax: int
    # Ширина ДНА, градусы
    dnay: int  # по оси y
    dnaz: int  # по оси x


class test:
    figext: int
    Xcr: float
    Zcr: float
    Nadir: int
    SWT: int
    pF: int
    pN: int
    cycleN = 0
    n_figs = 7
    hn_figs = 0
    scrsz = 0  # TODO не знаю что это
    cash_Enabled = 0
    mem_i = -1
    fpos = [1, 1, 576, 512]
    fstep = [100, 24]


class St:
    N: int
    Xs = "evs(Tr.Xa)+20"
    Ys = "evs(Tr.Ya)"
    Zs = "evs(Tr.Za)"
    Vx = "-evs(Tr.Vx)"
    Vy: str = "0"
    Vz: str = "0"
    tang: str = "0"
    kren: str = "0"
    psi: str = "0"
    Model: str = "0"
    Type: str = "1"
    wx: int
    wh: int
    wz: int
    RSC: int
    Pos = np.array([])


class Tr:
    Xa: str = "0"
    Ya: str = "100"
    Za: str = "0"
    Vx: str = "100"
    Vy: str = "0"
    Vz: str = "0"
    tang: str = "30"
    kren: str = "0"
    psi: str = "0"
    Pos = np.array([])
    Ang = None


class Sf:
    Relief: str
    Kspot: float
    KspotN: float
    WindTh: int
    WindFi: int
    AirT: int
    TownD: int
    XZstep: int
    maxY: int
    Elev: int
    Dspot: int
    x: int
    z: int
    rad_mul: float
    x_size: int
    z_size: int
    med_shift: float
    n: int
    Color = [
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
    Color_name = {
        10: "ground",
        20: "water",
        30: "meadow",
        40: "forest",
        50: "snow",
        60: "sand",
        70: "road",
        80: "bushes",
    }


class Sea:
    rho: int
    WindV: int
    WaveL: int
    Shift: int
    depth: int
    nr: int


def Relief():
    pass
