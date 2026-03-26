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
    Lambda: float = 0.0   # средняя длина волны, м
    Tm: float = 1e-2      # период модуляции/повторения импульсов
    dR: float = 0.0       # шаг по дальности
    x: list = field(default_factory=lambda: [0.2, -0.2,  0.0,  0.0])  # позиции ФЦ АС РЛС по x
    z: list = field(default_factory=lambda: [0.0,  0.0,  0.2, -0.2])  # позиции ФЦ АС РЛС по z


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
    dnay: int = 0  # ширина ДНА по оси y, градусы
    dnaz: int = 0  # ширина ДНА по оси x, градусы
    # Координаты излучателей МИ (заполняются в calc_mi_power)
    Z: np.ndarray = field(default_factory=lambda: np.array([50, -50,  0,   0], dtype=float))
    Y: np.ndarray = field(default_factory=lambda: np.array([ 0,   0, 50, -50], dtype=float))
    # Весовые коэффициенты излучателей (1 — включён, 0 — выключен)
    a: np.ndarray = field(default_factory=lambda: np.array([1, 1, 1, 1], dtype=float))
    # Относительные мощности излучателей (результат расчёта)
    Pi: np.ndarray = field(default_factory=lambda: np.array([1, 1, 1, 1], dtype=float))
    # Геометрия антенн МИ (заполняются в get_mixyz)
    sx: np.ndarray = field(default_factory=lambda: np.array([]))   # центральные позиции по X
    sz: np.ndarray = field(default_factory=lambda: np.array([]))   # центральные позиции по Z
    Mx: np.ndarray = field(default_factory=lambda: np.array([]))   # координаты антенн по X (м)
    Mz: np.ndarray = field(default_factory=lambda: np.array([]))   # координаты антенн по Z (м)
    My: np.ndarray = field(default_factory=lambda: np.array([]))   # координаты антенн по Y (м)
    Ax: np.ndarray = field(default_factory=lambda: np.array([]))   # угловые координаты по X (рад)
    Az: np.ndarray = field(default_factory=lambda: np.array([]))   # угловые координаты по Z (рад)
    Rt: np.ndarray = field(default_factory=lambda: np.array([]))   # расстояния до антенн (м)
    Dists: np.ndarray = field(default_factory=lambda: np.array([]))  # расстояния до центра АС РЛС
    Diffs: np.ndarray = field(default_factory=lambda: np.array([]))  # для расчёта выравнивающих кабелей
    dDist: float = 0.0    # максимальная разница расстояний
    Ants: int = 0         # счётчик — кол-во антенных элементов МИ


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
    Pos: np.ndarray = field(default_factory=lambda: np.zeros((1, 3)))
    Ang: object = None
    # Поля заполняются в get_traekt
    H1: float = 0.0          # начальная высота
    N: int = 0               # фактическая длина траектории
    t: np.ndarray = field(default_factory=lambda: np.array([]))
    V: np.ndarray = field(default_factory=lambda: np.zeros((1, 3)))
    Tm: np.ndarray = field(default_factory=lambda: np.array([]))
    Ti: np.ndarray = field(default_factory=lambda: np.array([]))
    Tm_Ni: np.ndarray = field(default_factory=lambda: np.array([]))
    Tm_i: np.ndarray = field(default_factory=lambda: np.array([]))
    TiT: np.ndarray = field(default_factory=lambda: np.array([]))
    TiR: np.ndarray = field(default_factory=lambda: np.array([]))
    Pz: np.ndarray = field(default_factory=lambda: np.array([]))
    Lx: list = field(default_factory=lambda: [0.0, 0.0])
    Lz: list = field(default_factory=lambda: [0.0, 0.0])
    Lh: list = field(default_factory=lambda: [0.0, 0.0])
    dR: float = 0.0          # шаг по дальности


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
    Pos: np.ndarray = field(default_factory=lambda: np.zeros((1, 3, 1)))
    # Поля заполняются в get_traekt
    V: np.ndarray = field(default_factory=lambda: np.zeros((1, 3, 1)))
    Ang: np.ndarray = field(default_factory=lambda: np.zeros((1, 3, 1)))


@dataclass
class consts:
    g: float = 9.80665   # ускорение свободного падения, м/с²
    delta: float = 1e-6  # дельта погрешности округлений мл. разрядов
    Pi2: float = field(default_factory=lambda: np.pi * 2)
    Pi4: float = field(default_factory=lambda: np.pi * 4)
    Pi4p3: float = field(default_factory=lambda: (np.pi * 4) ** 3)


@dataclass
class test:
    cycleN: int = 0       # число рассчитанных шагов (для циклического выполнения)
    n_figs: int = 7       # допустимое число фигур для данной версии ПО модели
    h: list = field(default_factory=lambda: [0, 0, 0, 0, 0, 0, 0, 0])  # указатели на фигуры
    scrsz: list = field(default_factory=lambda: [1, 1, 1680, 1050])     # ScreenSize [left,bottom,width,height]
    fpos: list = field(default_factory=lambda: [1, 1, 576, 512])        # базовое положение+размер окон
    fstep: list = field(default_factory=lambda: [100, 24])              # шаг автосмещения фигур по x,y
    # Меняющиеся параметры
    figext: int = 0
    Xcr: float = 0.0
    Zcr: float = 0.0
    Nadir: int = 0
    SWT: int = 0
    SwT: int = 1          # показывать траекторию на графике поверхности
    pF: int = 0
    pN: int = 0
    canceling: int = 0    # флаг отмены расчёта траектории


@dataclass
class Sf:
    Relief: str = ""
    Kspot: float = 0.0
    KspotN: float = 0.0
    WindTh: int = 0
    WindFi: int = 0
    WindV: float = 0.0    # скорость ветра, м/с
    AirT: int = 0
    TownD: int = 10       # плотность застройки города
    XZstep: int = 0
    maxY: int = 0
    Elev: int = 0
    Dspot: float = 0.0    # радиус пятна облучения
    x: int = 0
    z: int = 0
    rad_mul: float = 0.0
    x_size: int = 0
    z_size: int = 0
    med_shift: float = 0.0
    n: int = 0
    # Параметры леса
    TreeT: int = 1        # тип леса: 1=хвойный, 2=лиственный, 3=без листвы, 4=смешанный, 5=многоярусный
    TreeD: int = 80       # плотность леса, %
    LevH: np.ndarray = field(default_factory=lambda: np.array([0.2, 0.4, 0.6, 0.8, 1.0]))
    LevdH: np.ndarray = field(default_factory=lambda: np.array([0.7, 0.9, 1.0, 0.8, 0.4]))
    DORF: np.ndarray = field(default_factory=lambda: np.array([0.7, 0.9, 1.0, 1.2, 1.4]))
    KrF: np.ndarray = field(default_factory=lambda: np.array([0.7, 0.9, 1.0, 0.8, 0.4]))
    Types: np.ndarray = field(default_factory=lambda: np.zeros(10, dtype=int))  # счётчики по типам
    # Константы для автопостроения
    Color: list = field(default_factory=lambda: [
        10, 0.412, 0.267, 0.141,   # грунт
        20, 0.678, 0.922, 1.0,     # вода
        30, 0.467, 0.675, 0.188,   # луг/трава
        40, 0.231, 0.443, 0.337,   # лес
        50, 0.8,   0.8,   0.8,     # снег/скалы
        60, 0.929, 0.694, 0.125,   # песок/солончак
        70, 0.392, 0.475, 0.635,   # дорога/город
        80, 0.871, 0.49,  0.0,     # кустарник/прочее
    ])
    Color_name: dict = field(default_factory=lambda: {
        10: "ground",   # грунт
        20: "water",    # вода
        30: "meadow",   # луг/трава
        40: "forest",   # лес
        50: "snow",     # снег/скалы
        60: "sand",     # песок
        70: "road",     # дорога/город
        80: "bushes",   # кустарник/прочее
    })


@dataclass
class Sea:
    rho: int = 0
    WindV: int = 0
    WaveL: int = 0
    Shift: int = 0
    depth: int = 0
    nr: int = 0
    strenght: str = ""    # сила волнения (текстовое описание)