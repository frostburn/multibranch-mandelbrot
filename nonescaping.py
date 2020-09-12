from operator import add
from functools import reduce
from threading import Thread, Lock
from util import get_mesh, threaded_anti_alias
from pylab import *


def _eval(z, c, numerator, denominator, max_iter, leaf_map, operator):
    if max_iter == 0:
        return leaf_map(z)
    theta = 2*pi*arange(denominator) / denominator
    exponent = (numerator / denominator)
    if exponent < 0:
        z += (z==0)
    results = [_eval(exp(1j*t)*z**exponent + c, c, numerator, denominator, max_iter-1, leaf_map, operator) for t in theta]
    return reduce(operator, results)


def mandelbrot(width, height, center_x, center_y, zoom, rotation, numerator, denominator, max_iter, leaf_map, color_map, operator=add, anti_aliasing=2, julia_c=1j, julia=False):
    def generate_subpixel_image(offset_x, offset_y):
        x, y = get_mesh(width, height, center_x, center_y, zoom, rotation, offset_x, offset_y)
        z = x + 1j*y
        if julia:
            c = julia_c
        else:
            c = z

        return color_map(_eval(z, c, numerator, denominator, max_iter, leaf_map, operator))

    return threaded_anti_alias(generate_subpixel_image, width, height, anti_aliasing)


def _eval_dz(z, dz, c, dc, numerator, denominator, max_iter, leaf_map, operator):
    if max_iter == 0:
        return leaf_map(z, dz)
    spinors = exp(2j*pi*arange(denominator) / denominator)
    exponent = (numerator / denominator)
    z0 = z + (z==0)
    if exponent < 0:
        z = z0
    results = [_eval_dz(s*z**exponent + c, dz*s*exponent*z0**(exponent-1) + dc, c, dc, numerator, denominator, max_iter-1, leaf_map, operator) for s in spinors]
    return reduce(operator, results)


def mandelbrot_dx(width, height, center_x, center_y, zoom, rotation, numerator, denominator, max_iter, leaf_map, color_map, operator=add, anti_aliasing=2, julia_c=1j, julia=False):
    def generate_subpixel_image(offset_x, offset_y):
        x, y = get_mesh(width, height, center_x, center_y, zoom, rotation, offset_x, offset_y)
        z = x + 1j*y
        dz = 1 + 0j*z
        if julia:
            c = julia_c
            dc = 0
        else:
            c = z
            dc = 1

        return color_map(_eval_dz(z, dz, c, dc, numerator, denominator, max_iter, leaf_map, operator))

    return threaded_anti_alias(generate_subpixel_image, width, height, anti_aliasing)
