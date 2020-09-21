import os
import sys
sys.path.insert(0, os.path.abspath('.'))

from pylab import *
from mandelbrot import mandelbrot, mandelbrot_generic, buddhabrot
import nonescaping
import classic
from coloring import red_lavender, black_multi_edge, rainbow, gray, sepia, subharmonics, creature, white_multi_edge
from scipy.ndimage import gaussian_filter


def make_picture_frame(rgb, dither=1.0/256.0):
    if dither:
        rgb = [channel + random(channel.shape)*dither for channel in rgb]
    frame = stack(rgb, axis=-1)
    frame = clip(frame, 0.0, 1.0)
    return frame


if __name__ == '__main__':
    scale = 90
    width, height = 7*scale, 12*scale

    anti_aliasing = 5

    max_iter = 9

    zoom = -1.25
    rotation = -pi*0.5
    x, y = 0.8, 0.001
    light_height = 1.2
    light_angle = -0.2
    light_x = cos(light_angle)
    light_y = sin(light_angle)

    light2_height = 0.1
    light2_angle = 3.1
    light2_x = cos(light2_angle)
    light2_y = sin(light2_angle)

    def leaf_map(z, dz):
        return abs(z), z*dz.conjugate()

    def operator(t1, t2):
        return minimum(t1[0], t2[0]), where(t1[0] < t2[0], t1[1], t2[1])

    def color_map(t):
        r = t[0]
        dz = t[1]
        dx = real(dz)
        dy = imag(dz)
        dz = 0.4
        r = sqrt(dx*dx + dy*dy + dz*dz)
        dx /= r
        dy /= r
        dz /= r
        l = maximum(0.0, (light_x*dx + light_y*dy + dz*light_height) / (1 + light_height))
        l2 = maximum(0.0, (light2_x*dx + light2_y*dy + dz*light2_height) / (1 + light2_height))
        return minimum(1, array([0.5*r+0.5 - l2*0.1, 0.3*r+0.1 + sin(r*12)*0.1, 0.1*r+0.1 + sin(r*12-1.1)*0.1 + l2*0.1])*maximum(0.04, (l+l2 + sin(r*12)*0.1)**3*4))

    image = nonescaping.mandelbrot_dx(width, height, x, y, zoom, rotation, 1, 2, max_iter, color_map=color_map, leaf_map=leaf_map, operator=operator, anti_aliasing=anti_aliasing)

    imsave("/tmp/rose_emissary.png", make_picture_frame(image))
