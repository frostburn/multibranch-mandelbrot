from operator import add
from functools import reduce
from threading import Thread, Lock
from pylab import *


def _eval(z, c, numerator, denominator, max_iter, color_map, operator):
    if max_iter == 0:
        return color_map(z)
    z = z + c
    theta = 2*pi*arange(denominator) / denominator
    exponent = (numerator / denominator)
    if exponent < 0:
        z += (z==0)
    results = [_eval(exp(1j*t)*z**exponent + c, c, numerator, denominator, max_iter-1, color_map, operator) for t in theta]
    return reduce(operator, results)


def mandelbrot(width, height, center_x, center_y, zoom, rotation, numerator, denominator, max_iter, color_map, operator=add, anti_aliasing=2, julia_c=1j, julia=False):
    lock = Lock()

    num_color_channels = 3
    result = np.zeros((num_color_channels, height, width))

    c_, s_ = np.cos(rotation), np.sin(rotation)
    zoom = 2**-zoom / height
    def accumulate_subpixels(offset_x, offset_y):
        nonlocal result
        x = np.arange(width, dtype='float64') + offset_x
        y = np.arange(height, dtype='float64') + offset_y

        x, y = np.meshgrid(x, y)

        x = (2 * x - width) * zoom
        y = (2 * y - height) * zoom

        x, y = x*c_ + y*s_, y*c_ - x*s_
        x += center_x
        y += center_y

        z = x + 1j*y
        if julia:
            c = julia_c
        else:
            c = z

        subpixel_image = _eval(z, c, numerator, denominator, max_iter, color_map, operator)

        lock.acquire()
        result += subpixel_image
        lock.release()

    ts = []
    offsets = np.arange(anti_aliasing) / anti_aliasing
    for i in offsets:
        for j in offsets:
            ts.append(Thread(target=accumulate_subpixels, args=(i, j)))
            ts[-1].start()
    for t in ts:
        t.join()

    result /= anti_aliasing**2

    return result
