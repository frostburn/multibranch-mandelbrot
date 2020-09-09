from pylab import *
from mandelbrot import mandelbrot, mandelbrot_generic
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
    # Desktop
    width, height = 192*scale, 108*scale
    # Instagram
    # width, height = 108*scale, 108*scale

    anti_aliasing = 4
    max_iter = 7
    # color_map = red_lavender
    # color_map = black_multi_edge
    # color_map = rainbow
    # color_map = gray
    # color_map = sepia
    # color_map = subharmonics
    # color_map = creature

    zoom = -1
    x, y = 0, 0

    # image = mandelbrot(width, height, x, y, zoom, 3.5, max_iter, color_map=color_map, anti_aliasing=anti_aliasing, inside_cutoff=1024, clip_outside=True)
    # image = mandelbrot_generic(
    #     width, height, x, y, zoom, 3*pi/4,
    #     4, 2,
    #     max_iter, color_map=white_multi_edge, anti_aliasing=anti_aliasing, inside_cutoff=0, outside_offset=-3.5, clip_outside=False,
    #     julia_c=(randn() + randn()*1j), julia=False
    # )


    # def color_map(i):
    #     return clip(array([i*0.02, i*0.05, i*0.07]), 0, 1)

    # image = classic.mandelbrot(
    #     width, height, x, y, zoom, pi/2,
    #     2, exp(2j*pi*randint(0,2,max_iter)/2),
    #     anti_aliasing=anti_aliasing, color_map=color_map
    # )

    image = None

    for i in range(5):
        np.random.seed(i)
        c1, c2, c3, c4, c5 = np.random.rand(5)

        def leaf_map(z):
            return abs(z)
            # return (abs(z), z)

        def operator(t1, t2):
            return t1 + t2
            # min_r = t1[0] > t2[0]
            # return (where(min_r, t1[0], t2[0]), where(min_r, t1[1], t2[1]))


        def color_map(t):
            z = t
            # theta = angle(z)
            # rgb = array([0.28*abs(z+0.2) - 200*theta**2, 0.4*abs(z-0.1j+0.2) + cos(theta)*10, 0.1*abs(z-0.15+0.1j)**1.2 + theta*100])
            r = abs(z)-130
            rgb = array([r*c1, r*c2, r*c3])
            return rgb*0.0007

        image_ = nonescaping.mandelbrot(
            width, height, x, y, zoom, pi,
            -3, 2,
            max_iter, anti_aliasing=anti_aliasing,
            leaf_map=leaf_map, operator=operator, color_map=color_map,
            julia=True, julia_c=(0.5*c4 + 0.5*c5*1j)
        )

        if image is None:
            image = maximum(0, image_)
        else:
            image += maximum(0, image_)

    # def leaf_map_bloom(z):
    #      return abs(z)

    # def operator_bloom(a, b):
    #     return a + b

    # def color_map_bloom(m):
    #     return (array([0.2*m, 0.1*m, 0.05*m])*0.0001)**2

    # bloom = nonescaping.mandelbrot(
    #     width, height, x, y+0.1, zoom, pi/4,
    #     -11, 4,
    #     max_iter, anti_aliasing=anti_aliasing,
    #     leaf_map=leaf_map_bloom, operator=operator_bloom, color_map=color_map_bloom
    # )

    # image = maximum(0, image) + bloom
    # image *= 0.1
    # image += gaussian_filter(bloom, sigma=2*scale)**3

    imsave("/tmp/out.png", make_picture_frame(image))
