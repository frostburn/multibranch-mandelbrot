import numpy as np
from _routines import ffi, lib
from util import get_mesh, threaded_anti_alias, gradient_vector
from threading import Thread, Lock


def escape_time(z, c, exponent, twisors, escaped, inside, inside_operator):
    for i, t in enumerate(twisors):
        escaped[np.logical_and(escaped < 0, abs(z) >= 128)] = i
        s = escaped < 0
        z[s] = t*z[s]**exponent + c[s]
        inside[s] = inside_operator(inside[s], z[s])


def mandelbrot(width, height, center_x, center_y, zoom, rotation, exponent, twisors, inside_zero, inside_operator, inside_color_map, outside_color_map, anti_aliasing=2, julia_c=1j, julia=False):
    if isinstance(twisors, int):
        twisors = [1] * twisors

    def generate_subpixel_image(offset_x, offset_y):
        x, y = get_mesh(width, height, center_x, center_y, zoom, rotation, offset_x, offset_y)
        z = x + 1j*y
        inside = inside_operator(inside_zero, z)
        outside = x*0 - 1
        if julia:
            escape_time(z, z*0 + julia_c, exponent, twisors, outside, inside, inside_operator)
        else:
            escape_time(z, z+0, exponent, twisors, outside, inside, inside_operator)

        w = outside > 0
        outside[w] = np.log(np.log(abs(z[w]))) / np.log(exponent) - outside[w] + len(twisors) - 1 - np.log(np.log(128)) / np.log(exponent)
        outside[~w] = 0

        result = outside_color_map(outside)
        result[:,~w] = inside_color_map(inside[~w])
        return result

    return threaded_anti_alias(generate_subpixel_image, width, height, anti_aliasing)


def escape_time_dz(z, dz, c, dc, exponent, max_iter, escaped, inside, inside_operator):
    for i in range(max_iter):
        escaped[np.logical_and(escaped < 0, abs(z) >= 128)] = i
        s = escaped < 0
        dz[s] = dz[s]*exponent*z[s]**(exponent-1) + dc[s]
        z[s] = z[s]**exponent + c[s]
        if isinstance(inside, (tuple, list)):
            sliced = [t[s] for t in inside]
            result = inside_operator(sliced, z[s]+0, dz[s]+0)
            for t, r in zip(inside, result):
                t[s] = r
        else:
            inside[s] = inside_operator(inside[s], z[s], dz[s])


def mandelbrot_dx(width, height, center_x, center_y, zoom, rotation, exponent, max_iter, inside_zero, inside_operator, inside_color_map, outside_color_map, anti_aliasing=2, julia_c=1j, julia=False):
    def generate_subpixel_image(offset_x, offset_y):
        x, y = get_mesh(width, height, center_x, center_y, zoom, rotation, offset_x, offset_y)
        z = x + 1j*y
        dz = 1 + 0j*z
        inside = inside_operator(inside_zero, z, dz)
        outside = x*0 - 1
        if julia:
            escape_time_dz(z, dz, z*0 + julia_c, z*0, exponent, max_iter, outside, inside, inside_operator)
        else:
            escape_time_dz(z, dz, z+0, 1 + z*0, exponent, max_iter, outside, inside, inside_operator)

        u = dz*z.conjugate()
        u /= abs(u)

        w = outside > 0
        outside[w] = np.log(np.log(abs(z[w]))) / np.log(exponent) - outside[w] + max_iter - 1 - np.log(np.log(128)) / np.log(exponent)
        outside[~w] = 0

        result = outside_color_map(outside, np.real(u), np.imag(u))
        result[:,~w] = inside_color_map(inside)[:, ~w]
        return result

    return threaded_anti_alias(generate_subpixel_image, width, height, anti_aliasing)
