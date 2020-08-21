from pylab import *
from mandelbrot import mandelbrot, mandelbrot_generic
import nonescaping
from coloring import red_lavender, black_multi_edge, rainbow, gray, sepia, subharmonics, creature
from scipy.ndimage import gaussian_filter


def make_picture_frame(rgb, dither=1.0/256.0):
    if dither:
        rgb = [channel + random(channel.shape)*dither for channel in rgb]
    frame = stack(rgb, axis=-1)
    frame = clip(frame, 0.0, 1.0)
    return frame


if __name__ == '__main__':
    scale = 10
    # Desktop
    width, height = 192*scale, 108*scale
    # Instagram
    width, height = 108*scale, 108*scale

    anti_aliasing = 5
    max_iter = 7
    # color_map = red_lavender
    # color_map = black_multi_edge
    # color_map = rainbow
    # color_map = gray
    # color_map = sepia
    # color_map = subharmonics
    # color_map = creature

    x, y = 0.001, -2**-1.25
    zoom = 1.25

    # image = mandelbrot(width, height, x, y, zoom, 3.5, max_iter, color_map=color_map, anti_aliasing=anti_aliasing, inside_cutoff=1024, clip_outside=True)
    # image = mandelbrot_generic(
    #     width, height, x, y, zoom, -pi/2,
    #     4, 3,
    #     max_iter, color_map=creature, anti_aliasing=anti_aliasing, inside_cutoff=2**15, outside_offset=0, clip_outside=True,
    #     julia_c=(randn() + randn()*1j), julia=False
    # )

    def leaf_map(z):
        return (abs(abs(z)-0.4), z)

    def operator(t1, t2):
        min_r = t1[0] < t2[0]
        return (where(min_r, t1[0], t2[0]), where(min_r, t1[1], t2[1]))

    def color_map(t):
        z = t[1]
        rgb = array([0.4*abs(z+0.2)**2, 0.7*abs(z-1j), 0.5*abs(z-1-1j)]) + exp(-5*(abs(z)-2)**2)
        return rgb

    image = nonescaping.mandelbrot(
        width, height, x, y, zoom, 0,
        1, 3,
        max_iter, anti_aliasing=anti_aliasing,
        leaf_map=leaf_map, operator=operator, color_map=color_map
    )

    # image += 0.5*gaussian_filter(image**2, sigma=2*scale)**0.5

    imsave("/tmp/out.png", make_picture_frame(image))
