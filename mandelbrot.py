import numpy as np
from _routines import ffi, lib
from threading import Thread, Lock

def mandelbrot(width, height, x, y, zoom, exponent, max_iter, inside_cutoff=2048, outside_cutoff=0, clip_outside=True, anti_aliasing=2):
    inside_lock = Lock()
    outside_lock = Lock()

    inside = np.zeros(height * width)
    outside = np.zeros(height * width)

    def accumulate_subpixels(offset_x, offset_y):
        nonlocal inside, outside
        inside_arr = np.empty(height * width, dtype='int64')
        outside_arr = np.empty(height * width, dtype='float64')
        inside_buf = ffi.cast("long long*", inside_arr.ctypes.data)
        outside_buf = ffi.cast("double*", outside_arr.ctypes.data)
        lib.mandelbrot(inside_buf, outside_buf, width, height, offset_x, offset_y, x, y, zoom, int(exponent - 0.5), max_iter, inside_cutoff, outside_cutoff)
        if clip_outside:
            outside_arr *= (inside_arr == 0)
        inside_lock.acquire()
        inside += inside_arr
        inside_lock.release()
        outside_lock.acquire()
        outside += outside_arr
        outside_lock.release()

    ts = []
    offsets = np.arange(anti_aliasing) / anti_aliasing
    for i in offsets:
        for j in offsets:
            ts.append(Thread(target=accumulate_subpixels, args=(i, j)))
            ts[-1].start()
    for t in ts:
        t.join()

    inside /= anti_aliasing**2
    outside /= anti_aliasing**2

    return inside.reshape(height, width), outside.reshape(height, width)
