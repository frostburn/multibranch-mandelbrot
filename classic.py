import numpy as np
from _routines import ffi, lib
from util import get_mesh, threaded_anti_alias
from threading import Thread, Lock


EPSILON = 1e-12


def escape_time(z, c, exponent, twisors, escaped):
    for i, t in enumerate(twisors):
        escaped[np.logical_and(escaped < 0, abs(z) >= 128)] = i
        s = escaped < 0
        z[s] = t*z[s]**exponent + c[s]


def mandelbrot(width, height, center_x, center_y, zoom, rotation, exponent, twisors, color_map, anti_aliasing=2, julia_c=1j, julia=False):
    lock = Lock()

    num_color_channels = 3
    result = np.zeros((num_color_channels, height, width))

    c, s = np.cos(rotation), np.sin(rotation)
    zoom = 2**-zoom / height
    def accumulate_subpixels(offset_x, offset_y):
        nonlocal result
        x = np.arange(width, dtype='float64') + offset_x
        y = np.arange(height, dtype='float64') + offset_y

        x, y = np.meshgrid(x, y)

        x = (2 * x - width) * zoom
        y = (2 * y - height) * zoom

        x, y = x*c + y*s, y*c - x*s
        x += center_x
        y += center_y

        z = x + 1j*y
        outside = x*0 - 1
        if julia:
            escape_time(z, z*0 + julia_c, exponent, twisors, outside)
        else:
            escape_time(z, z+0, exponent, twisors, outside)

        w = outside > 0
        outside[w] -= np.log(np.log(abs(z[w]))) / np.log(exponent)
        outside[~w] = len(twisors) - np.log(np.log(128)*2) / np.log(exponent)  # TODO: Fix

        subpixel_image = color_map(outside)

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


def escape_time_dz(z, dz, c, dc, exponent, escaped, max_iter):
    for i in range(max_iter):
        escaped[np.logical_and(escaped < 0, abs(z) >= 128)] = i
        s = escaped < 0
        dz[s] = dz[s]*exponent*z[s]**(exponent-1) + dc[s]
        z[s] = z[s]**exponent + c[s]


def mandelbrot_dx(width, height, center_x, center_y, zoom, rotation, exponent, max_iter, color_map, anti_aliasing=2, julia_c=1j, julia=False):
    def generate_subpixel_image(offset_x, offset_y):
        x, y = get_mesh(width, height, center_x, center_y, zoom, rotation, offset_x, offset_y)
        z = x + 1j*y
        dz = 1 + 0j*z
        outside = x*0 - 1
        if julia:
            escape_time_dz(z, dz, z*0 + julia_c, z*0, exponent, outside, max_iter)
        else:
            escape_time_dz(z, dz, z+0, 1 + z*0, exponent, outside, max_iter)

        r = abs(z)
        u = dz/(z + (r < EPSILON))
        ru = abs(u)
        u /= ru + (ru < EPSILON)

        w = outside > 0
        outside[w] = np.log(np.log(r[w])) / np.log(exponent) - outside[w] + max_iter - 1 - np.log(np.log(128)) / np.log(exponent)
        outside[~w] = 0

        return color_map(outside, np.real(u), np.imag(u))

    return threaded_anti_alias(generate_subpixel_image, width, height, anti_aliasing)
