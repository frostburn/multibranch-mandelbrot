import numpy as np
from _routines import ffi, lib
from threading import Thread, Lock

def mandelbrot(width, height, x, y, zoom, exponent, max_iter, color_map, inside_cutoff=2048, clip_outside=False, anti_aliasing=2):
    lock = Lock()

    num_color_channels = 3
    result = np.zeros((num_color_channels, height, width))

    def accumulate_subpixels(offset_x, offset_y):
        nonlocal result
        inside_arr = np.empty(height * width, dtype='int64')
        outside_arr = np.empty(height * width, dtype='float64')
        inside_buf = ffi.cast("long long*", inside_arr.ctypes.data)
        outside_buf = ffi.cast("double*", outside_arr.ctypes.data)
        lib.mandelbrot(inside_buf, outside_buf, width, height, offset_x, offset_y, x, y, zoom, int(exponent - 0.5), max_iter, inside_cutoff, clip_outside)

        subpixel_image = color_map(inside_arr.reshape(height, width), outside_arr.reshape(height, width), inside_cutoff)

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


def mandelbrot_generic(width, height, center_x, center_y, zoom, rotation, numerator, denominator, max_iter, color_map, inside_cutoff=2048, outside_offset=0.0, anti_aliasing=2, julia_c=1j, julia=False):
    lock = Lock()

    num_color_channels = 3
    result = np.zeros((num_color_channels, height, width))

    c, s = np.cos(rotation), np.sin(rotation)
    z = 2**-zoom / height
    def accumulate_subpixels(offset_x, offset_y):
        nonlocal result
        x = np.arange(width, dtype='float64') + offset_x
        y = np.arange(height, dtype='float64') + offset_y

        x, y = np.meshgrid(x, y)

        x = (2 * x - width) * z
        y = (2 * y - height) * z

        x, y = x*c + y*s, y*c - x*s
        x += center_x
        y += center_y

        x_buf = ffi.cast("double*", x.ctypes.data)
        y_buf = ffi.cast("double*", y.ctypes.data)
        lib.mandelbrot_generic(x_buf, y_buf, width*height, numerator, denominator, max_iter, inside_cutoff, outside_offset, np.real(julia_c), np.imag(julia_c), julia)
        inside = x
        outside = y

        subpixel_image = color_map(inside, outside, inside_cutoff)

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
