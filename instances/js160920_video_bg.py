# A hack so that I don't have to make anything installable, but can still organize things into folders.
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
    scale = 10
    # Youtube
    width, height = 192*scale, 108*scale

    anti_aliasing = 4
    max_iter = 7

    zoom = 1
    x, y = -0.65, 0.85
    rotation = pi

    image = None

    for i in range(7):
        np.random.seed(i+108)
        c1, c2, c3, c4, c5 = np.random.rand(5)

        julia_c = (c4 + c5*1j) * 0.9

        def leaf_map(z):
            return abs(z - julia_c)

        def operator(r1, r2):
            return r1 + r2

        def color_map(r):
            r -= 150
            rgb = array([r*c1, r*c2, r*c3])
            return rgb*0.0005

        image_ = nonescaping.mandelbrot(
            width, height, x, y, zoom, rotation,
            -5, 2,
            max_iter, anti_aliasing=anti_aliasing,
            leaf_map=leaf_map, operator=operator, color_map=color_map,
            julia=True, julia_c=julia_c
        )

        if image is None:
            image = maximum(0, image_)
        else:
            image += maximum(0, image_)

    imsave("/tmp/out.png", make_picture_frame(image))
