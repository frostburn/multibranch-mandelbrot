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

    anti_aliasing = 4
    max_iter = 7
    # color_map = red_lavender
    # color_map = black_multi_edge
    # color_map = rainbow
    # color_map = gray
    # color_map = sepia
    # color_map = subharmonics
    # color_map = creature

    x, y = 0, 0
    zoom = 0

    # image = mandelbrot(width, height, x, y, zoom, 3.5, max_iter, color_map=color_map, anti_aliasing=anti_aliasing, inside_cutoff=1024, clip_outside=True)
    # edges = mandelbrot_generic(
    #     width, height, x, y, zoom, -pi/2,
    #     3, 2,
    #     max_iter, color_map=black_multi_edge, anti_aliasing=anti_aliasing, inside_cutoff=0, outside_offset=-2,
    #     julia_c=(randn() + randn()*1j), julia=False
    # )
    # fills = mandelbrot_generic(
    #     width, height, x, y, zoom, -pi/2,
    #     3, 2,
    #     max_iter-2, color_map=creature, anti_aliasing=anti_aliasing, inside_cutoff=0, outside_offset=-2,
    #     julia_c=(randn() + randn()*1j), julia=False
    # )
    # image = fills * edges

    def color_map(z):
        r = abs(z)
        theta = angle(z) * 5 + 2*r
        rgb = array([sin(theta), sin(theta+2*pi/3), sin(theta+4*pi/3)]) * 0.7 + 0.3
        return rgb * r**1.8 * 0.008

    image = nonescaping.mandelbrot(
        width, height, x, y, zoom, 0,
        -1, 2,
        max_iter, color_map, anti_aliasing=anti_aliasing
    )

    image += 0.5*gaussian_filter(image**2, sigma=2*scale)**0.5

    imsave("/tmp/out.png", make_picture_frame(image))
