import os
import sys
sys.path.insert(0, os.path.abspath('.'))

from pylab import *
from mandelbrot import mandelbrot, mandelbrot_generic, buddhabrot
import nonescaping
import classic
from coloring import red_lavender, black_multi_edge, rainbow, gray, sepia, subharmonics, creature, white_multi_edge
import color_gradients
from scipy.ndimage import gaussian_filter


def make_picture_frame(rgb, dither=1.0/256.0):
    if dither:
        rgb = [channel + random(channel.shape)*dither for channel in rgb]
    frame = stack(rgb, axis=-1)
    frame = clip(frame, 0.0, 1.0)
    return frame


if __name__ == '__main__':
    scale = 9*10
    width, height = 7*scale, 12*scale

    anti_aliasing = 6

    max_iter = 1<<9

    zoom = -0.8
    rotation = -0.1
    x, y = 0, 0.001

    def illuminate(dx, dy, dz=0.5, light_angle=0.5, light_elevation=1.2):
        r = sqrt(dx*dx + dy*dy + dz*dz)
        dx /= r
        dy /= r
        dz /= r
        return maximum(0.0, sin(light_elevation)*cos(light_angle)*dx + sin(light_elevation)*sin(light_angle)*dy + cos(light_elevation)*dz)

    inside_zero = (10000, 0j)

    def inside_operator(t, z, dz):
        min_r, min_dz = t
        return minimum(min_r, abs(z)), where(abs(z) < min_r, z*dz.conjugate(), min_dz)

    def inside_color_map(t):
        r, dz = t
        dz += 0.1*dz/abs(dz)
        l = illuminate(real(dz), imag(dz))
        return (color_gradients.platinum(1+r*3)*0.9 + array([r*0, exp(-4*r), -0.2*r*exp(-2*r)])) * (0.85*l + 0.1)

    def outside_color_map(outside, dx, dy):
        l = illuminate(dx, dy)
        return (color_gradients.platinum(outside) + array([15*exp(-(0.003*outside)**4), -10*exp(-(0.0028*outside)**4), -5*exp(-(0.0041*outside)**2)])) * (0.9*l + 0.1)

    image = classic.mandelbrot_dx(
        width, height, x, y, zoom, rotation, 6, max_iter,
        inside_zero=inside_zero,
        inside_operator=inside_operator,
        inside_color_map=inside_color_map,
        outside_color_map=outside_color_map,
        anti_aliasing=anti_aliasing,
        julia=True,
        julia_c=0.6889+0.44989j
    )

    imsave("/tmp/out.png", make_picture_frame(image))
