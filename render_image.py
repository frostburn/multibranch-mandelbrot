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
    scale = 10
    # Instagram
    width, height = 108*scale, 108*scale

    anti_aliasing = 3
    num_total_samples = 2**28

    max_iter = 5
    min_iter = max_iter - 1

    zoom = -3
    rotation = 0
    x, y = 0, 0.75

    # image = mandelbrot(width, height, x, y, zoom, 3.5, max_iter, color_map=color_map, anti_aliasing=anti_aliasing, inside_cutoff=1024, clip_outside=True)
    # image = mandelbrot_generic(
    #     width, height, x, y, zoom, 3*pi/4,
    #     4, 2,
    #     max_iter, color_map=white_multi_edge, anti_aliasing=anti_aliasing, inside_cutoff=0, outside_offset=-3.5, clip_outside=False,
    #     julia_c=(randn() + randn()*1j), julia=False
    # )

    image = []

    for channel in range(3):
        def generator(num_samples):
            theta = 2*pi*rand(num_samples)
            rr = randn(num_samples) * 0.003
            ri = randn(num_samples) * 0.003
            radius = 0.4 * exp(-channel*0.1)
            return 0.15 + radius*cos(theta) + rr + 1j*(0.2 + radius*sin(theta) + ri)

        exposure = buddhabrot(anti_aliasing*width, anti_aliasing*height, x, y, zoom, rotation, 5, 2, max_iter, min_iter, generator, num_total_samples, 16, julia=True)

        exposure = tanh((exposure * (0.4*width*height / num_total_samples)) ** 0.5)

        result = exposure[::anti_aliasing, ::anti_aliasing]*0
        for i in range(anti_aliasing):
            for j in range(anti_aliasing):
                result += exposure[i::anti_aliasing, j::anti_aliasing]
        result /= anti_aliasing**2
        image.append(result)
    image = array(image)

    imsave("/tmp/out.png", make_picture_frame(image))
