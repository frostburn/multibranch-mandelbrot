import os
import sys
sys.path.insert(0, os.path.abspath('.'))

from pylab import *
from mandelbrot import mandelbrot, mandelbrot_generic
import nonescaping
import classic
from coloring import red_lavender, black_multi_edge, rainbow, gray, sepia, subharmonics, creature, white_multi_edge
from scipy.ndimage import gaussian_filter

from render_image import make_picture_frame


if __name__ == '__main__':
    scale = 90
    width, height = 7*scale, 12*scale

    anti_aliasing = 4
    max_iter = 7
    zoom = -0.94
    x, y = 0, 0

    image = None

    for i in range(5):
        np.random.seed(i+2*108)
        c1, c2, c3, c4, c5 = np.random.rand(5)

        def leaf_map(z):
            return abs(z)

        def operator(t1, t2):
            return t1 + t2

        def color_map(t):
            z = t
            r = abs(z)-130
            rgb = array([0.61*r*c1, 0.1*r*c2, r*c3])
            return rgb*0.0081

        image_ = nonescaping.mandelbrot(
            width, height, x, y, zoom, 0.24*pi,
            -2, 2,
            max_iter, anti_aliasing=anti_aliasing,
            leaf_map=leaf_map, operator=operator, color_map=color_map,
            julia=True, julia_c=(0.5*c4 + 0.5*c5*1j)
        )

        if image is None:
            image = maximum(0, image_)
        else:
            image += maximum(0, image_)

    imsave("/tmp/out.png", make_picture_frame(image))
