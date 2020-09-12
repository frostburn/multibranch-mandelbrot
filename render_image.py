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

    anti_aliasing = 4
    # num_total_samples = 2**34

    max_iter = 9
    # min_iter = max_iter - 1

    zoom = -1
    rotation = -pi*0.5
    x, y = 0.75, 0
    light_height = 1.1
    light_angle = 0.4
    light_x = cos(light_angle)
    light_y = sin(light_angle)

    # def color_map(outside, dx, dy):
    #     l = (light_x*dx + light_y*dy + light_height) / (1 + light_height)
    #     return array([outside + 700*(outside==0), 0.5*outside + 2*(outside==0), 0.2*outside + 3*(outside==0)])*l*0.0008 + (outside==0)*0.05

    # image = classic.mandelbrot_dx(width, height, x, y, zoom, rotation, 2.0, max_iter, color_map=color_map, anti_aliasing=anti_aliasing)

    def leaf_map(z, dz):
        return abs(z), dz

    def operator(t1, t2):
        return minimum(t1[0], t2[0]), where(t1[0] < t2[0], t1[1], t2[1])

    def color_map(t):
        r = t[0]
        dz = t[1]
        dx = real(dz)
        dy = imag(dz)
        l = maximum(0, (light_x*dx + light_y*dy + light_height) / (1 + light_height))
        return array([0.5*r+0.5, 0.2*r+0.2 + sin(r*10)*0.1, 0.1*r+0.1 + sin(r*10-1.1)*0.2])*l*2

    image = nonescaping.mandelbrot_dx(width, height, x, y, zoom, rotation, 1, 2, max_iter, color_map=color_map, leaf_map=leaf_map, operator=operator, anti_aliasing=anti_aliasing)

    # image = mandelbrot_generic(
    #     width, height, x, y, zoom, 3*pi/4,
    #     4, 2,
    #     max_iter, color_map=white_multi_edge, anti_aliasing=anti_aliasing, inside_cutoff=0, outside_offset=-3.5, clip_outside=False,
    #     julia_c=(randn() + randn()*1j), julia=False
    # )

    # image = []

    # for channel in range(3):
    #     def generator(num_samples):
    #         return 4*rand(num_samples)-2 + 1j*(4*rand(num_samples)-2)

    #     exposure = buddhabrot(anti_aliasing*width, anti_aliasing*height, x, y, zoom, rotation, 3, 2, max_iter+channel, min_iter+channel, generator, num_total_samples, 16)

    #     exposure = tanh((exposure * ((channel+1)*15*width*height / num_total_samples))**0.8)

    #     result = exposure[::anti_aliasing, ::anti_aliasing]*0
    #     for i in range(anti_aliasing):
    #         for j in range(anti_aliasing):
    #             result += exposure[i::anti_aliasing, j::anti_aliasing]
    #     result /= anti_aliasing**2
    #     image.append(result)
    # image = array(image)

    imsave("/tmp/out.png", make_picture_frame(image))
