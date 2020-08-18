from pylab import *
from mandelbrot import mandelbrot, mandelbrot_generic
from coloring import red_lavender, black_multi_edge, rainbow, gray, sepia, subharmonics


def make_picture_frame(rgb, dither=1.0/256.0):
    if dither:
        rgb = [channel + random(channel.shape)*dither for channel in rgb]
    frame = stack(rgb, axis=-1)
    frame = clip(frame, 0.0, 1.0)
    return frame


if __name__ == '__main__':
    # Desktop
    width, height = 192*10, 108*10
    # Instagram
    width, height = 108*10, 108*10

    anti_aliasing = 8
    max_iter = 5
    # color_map = red_lavender
    color_map = black_multi_edge
    # color_map = rainbow
    # color_map = gray
    # color_map = sepia
    # color_map = subharmonics

    x, y = 0.11, 0
    zoom = -1

    # image = mandelbrot(width, height, x, y, zoom, 3.5, max_iter, color_map=color_map, anti_aliasing=anti_aliasing, inside_cutoff=1024, clip_outside=True)
    image = mandelbrot_generic(
        width, height, x, y, zoom, 0,
        5, 2,
        max_iter, color_map=color_map, anti_aliasing=anti_aliasing, inside_cutoff=0, outside_offset=-1.5,
        julia_c=(randn() + randn()*1j), julia=False
    )

    imsave("/tmp/out.png", make_picture_frame(image))
