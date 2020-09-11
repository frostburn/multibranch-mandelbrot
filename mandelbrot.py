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


def mandelbrot_generic(width, height, center_x, center_y, zoom, rotation, numerator, denominator, max_iter, color_map, inside_cutoff=2048, outside_offset=0.0, clip_outside=False, anti_aliasing=2, julia_c=1j, julia=False):
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
        lib.mandelbrot_generic(x_buf, y_buf, width*height, numerator, denominator, max_iter, inside_cutoff, outside_offset, clip_outside, np.real(julia_c), np.imag(julia_c), julia)
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


def buddhabrot(width, height, center_x, center_y, zoom, rotation, numerator, denominator, max_iter, min_iter, generator, num_samples, num_threads, bailout=16, chunk_size=8192, julia_c=1j, julia=False):
    num_color_channels = 3
    result = np.zeros((height, width), dtype="uint64")
    result_buf = ffi.cast("unsigned long long*", result.ctypes.data)

    num_samples = int(round(num_samples / num_threads))

    c, s = np.cos(rotation), np.sin(rotation)
    z = 2**zoom * height
    dx00 = z*c
    dx11 = z*c
    dx01 = z*s
    dx10 = -z*s
    x0 = width*0.5 - dx00 * center_x - dx01 * center_y
    y0 = height*0.5 - dx10 * center_x - dx11 * center_y
    def accumulate_samples():
        remaining = num_samples
        while remaining:
            chunk = min(remaining, chunk_size)
            samples = generator(chunk)
            samples_buf = ffi.cast("double*", samples.ctypes.data)
            if julia:
                cs = samples*0j + julia_c
            else:
                cs = samples
            cs_buf = ffi.cast("double*", cs.ctypes.data)
            seed = np.random.randint(0, 1<<32);
            lib.buddhabrot(samples_buf, cs_buf, chunk, result_buf, width, height, x0, y0, dx00, dx01, dx10, dx11, numerator, denominator, max_iter, min_iter, bailout, seed)
            remaining -= chunk

    ts = []
    for _ in range(num_threads):
        ts.append(Thread(target=accumulate_samples))
        ts[-1].start()
    for t in ts:
        t.join()

    return result
