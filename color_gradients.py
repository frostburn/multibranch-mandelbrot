import numpy as np
from scipy.interpolate import CubicSpline

def spline(x, y):
    return CubicSpline(x, y, bc_type='periodic', extrapolate='periodic')

_platinum_red = spline(
    np.array([0.0, 0.5, 0.8, 0.9, 1.0]),
    np.array([217, 229, 241, 250, 217]) / 255.0,
)
_platinum_green = spline(
    np.array([0.0, 0.49, 0.79, 0.91, 1.0]),
    np.array([216, 228, 240, 248, 216]) / 255.0,
)
_platinum_blue = spline(
    np.array([0.0, 0.51, 0.81, 0.89, 1.0]),
    np.array([214, 226, 237, 246, 214]) / 255.0,
)
def platinum(x):
    return np.array([_platinum_red(x), _platinum_green(x), _platinum_blue(x)])


current_state = np.random.get_state()

np.random.seed(1)
_pineapple_beach_channels = []
for _ in range(3):
    x = list(sorted(np.random.rand(4)))
    x.insert(0, 0.0)
    x.append(1.0)
    y = list(np.random.rand(5))
    y.append(y[0])
    _pineapple_beach_channels.append(spline(x, y))

def pineapple_beach(x):
    return np.array([c(x) for c in _pineapple_beach_channels])


np.random.seed(5)
_neon_candy_channels = []
for _ in range(3):
    x = list(sorted(np.random.rand(4)))
    x.insert(0, 0.0)
    x.append(1.0)
    y = list(np.random.rand(5))
    y.append(y[0])
    _neon_candy_channels.append(spline(x, y))

def neon_candy(x):
    return np.array([c(x) for c in _neon_candy_channels])


np.random.seed(11)
_oil_bubble_channels = []
for _ in range(3):
    x = list(sorted(np.random.rand(4)))
    x.insert(0, 0.0)
    x.append(1.0)
    y = list(np.random.rand(5))
    y.append(y[0])
    _oil_bubble_channels.append(spline(x, y))

def oil_bubble(x):
    return np.array([c(x) for c in _oil_bubble_channels])


np.random.seed(12)
_cool_channels = []
for _ in range(3):
    x = list(sorted(np.random.rand(5)))
    x.insert(0, 0.0)
    x.append(1.0)
    y = list(np.random.rand(6))
    y.append(y[0])
    _cool_channels.append(spline(x, y))

def cool(x):
    return np.array([c(x) for c in _cool_channels])

np.random.set_state(current_state)