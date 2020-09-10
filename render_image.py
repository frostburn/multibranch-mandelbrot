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
    num_total_samples = 2**33

    max_iter = 9
    min_iter = max_iter - 1

    zoom = 1.25
    rotation = 0
    x, y = 0, 0

    # image = mandelbrot(width, height, x, y, zoom, 3.5, max_iter, color_map=color_map, anti_aliasing=anti_aliasing, inside_cutoff=1024, clip_outside=True)
    # image = mandelbrot_generic(
    #     width, height, x, y, zoom, 3*pi/4,
    #     4, 2,
    #     max_iter, color_map=white_multi_edge, anti_aliasing=anti_aliasing, inside_cutoff=0, outside_offset=-3.5, clip_outside=False,
    #     julia_c=(randn() + randn()*1j), julia=False
    # )

    def generator(num_samples):
        orientation = np.random.randint(0, 3) * 2*np.pi / 3.0
        offset = np.random.randint(-15, 16) * 0.035 + np.random.randn(num_samples)*0.0005
        c = cos(orientation)
        s = sin(orientation)
        l = 4*np.random.rand(num_samples) - 2
        return c*l + s*offset + 1j*(c*offset - s*l)

    exposure = buddhabrot(anti_aliasing*width, anti_aliasing*height, x, y, zoom, rotation, 2, 1, max_iter, min_iter, generator, num_total_samples, 16)

    image = tanh((exposure * (3*width*height / num_total_samples)) ** 0.22)

    result = image[::anti_aliasing, ::anti_aliasing]*0
    for i in range(anti_aliasing):
        for j in range(anti_aliasing):
            result += image[i::anti_aliasing, j::anti_aliasing]
    result /= anti_aliasing**2
    image = array([result, result, result])

    imsave("/tmp/out.png", make_picture_frame(image))
