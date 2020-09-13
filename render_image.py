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
    scale = 5
    # Instagram
    width, height = 108*scale, 108*scale

    anti_aliasing = 4
    # num_total_samples = 2**34

    phi = (1 + sqrt(5)) * 0.5
    golden_angle = 2j*pi / phi
    max_iter = 1<<8
    # twisors = [exp(1j*pi*i) for i in range(max_iter)]
    twisors = max_iter
    # min_iter = max_iter - 1

    zoom = -0.5
    rotation = pi*0.5
    x, y = -0.12, 0.001
    # light_height = 1.2
    # light_angle = -0.2
    # light_x = cos(light_angle)
    # light_y = sin(light_angle)

    # light2_height = 0.1
    # light2_angle = 3.1
    # light2_x = cos(light2_angle)
    # light2_y = sin(light2_angle)

    # def color_map(outside, dx, dy):
    #     l = (light_x*dx + light_y*dy + light_height) / (1 + light_height)
    #     return array([outside + 700*(outside==0), 0.5*outside + 2*(outside==0), 0.2*outside + 3*(outside==0)])*l*0.0008 + (outside==0)*0.05

    inside_zero = 10000

    def inside_operator(min_r, z):
        return minimum(min_r, abs(z))

    def outside_color_map(outside):
        r, g, b = color_gradients.cool(outside**2 * 0.01)
        return 0.8 + 0.2*array([r+g, g+b, b])

    def inside_color_map(r):
        return color_gradients.platinum(r)

    image = classic.mandelbrot(
        width, height, x, y, zoom, rotation, 7, twisors,
        inside_zero=inside_zero,
        inside_operator=inside_operator,
        inside_color_map=inside_color_map,
        outside_color_map=outside_color_map,
        anti_aliasing=anti_aliasing
    )

    # def leaf_map(z, dz):
    #     return abs(z), z*dz.conjugate()

    # def operator(t1, t2):
    #     return minimum(t1[0], t2[0]), where(t1[0] < t2[0], t1[1], t2[1])

    # def color_map(t):
    #     r = t[0]
    #     dz = t[1]
    #     dx = real(dz)
    #     dy = imag(dz)
    #     dz = 0.4
    #     r = sqrt(dx*dx + dy*dy + dz*dz)
    #     dx /= r
    #     dy /= r
    #     dz /= r
    #     l = maximum(0.0, (light_x*dx + light_y*dy + dz*light_height) / (1 + light_height))
    #     l2 = maximum(0.0, (light2_x*dx + light2_y*dy + dz*light2_height) / (1 + light2_height))
    #     return array([0.5*r+0.5 - l2*0.1, 0.3*r+0.1 + sin(r*12)*0.1, 0.1*r+0.1 + sin(r*12-1.1)*0.1 + l2*0.1])*maximum(0.04, (l+l2 + sin(r*12)*0.1)**3*4)

    # image = nonescaping.mandelbrot_dx(width, height, x, y, zoom, rotation, 1, 2, max_iter, color_map=color_map, leaf_map=leaf_map, operator=operator, anti_aliasing=anti_aliasing, julia=False, julia_c=(0.4 - 0.42j))

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
