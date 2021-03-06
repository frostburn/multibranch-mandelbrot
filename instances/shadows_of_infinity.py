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
    scale = 10
    # Instagram
    width, height = 108*scale, 108*scale

    anti_aliasing = 2
    num_samples = 1<<25
    max_iter = 1<<10
    min_iter = 1<<9

    zoom = -1.7
    rotation = -pi*0.5
    x, y = -0.2, 0.001

    def circle_factory(theta, delta, radius=1.0, spread=0.5, x=0.0, y=0.08):
        def circle(num_samples):
            phi = rand(num_samples) - rand(num_samples)
            phi = theta + delta * phi
            r = radius + randn(num_samples) * spread
            return x + cos(phi) * r + 1j * (y + sin(phi) * r)
        return circle

    offset = 0.5
    delta = 3.5
    exposures = []
    num_layers = 1
    for i in range(num_layers):
        sub_exposures = [
            (3*i+min_iter, 3*i+max_iter, circle_factory(offset + j*2*pi/3, delta)) for j in range(3)
        ]
        exposures.extend(sub_exposures)

    def color_map(exposed):
        e = exposed[0]*0.0
        result = array([e, e, e])
        for i in range(num_layers):
            for j in range(3):
                result[j] += (3*scale**2*exposed[i*3 + j] * num_samples**-0.9)**0.78
        return result

    image = buddhabrot(width, height, x, y, zoom, rotation, -2, 1, num_samples, exposures, color_map, anti_aliasing=anti_aliasing, bailout=1e300)

    imsave("/tmp/out.png", make_picture_frame(image))
