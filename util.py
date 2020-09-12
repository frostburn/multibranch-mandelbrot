from threading import Thread, Lock
import numpy as np

def get_mesh(width, height, center_x, center_y, zoom, rotation, offset_x, offset_y):
    c, s = np.cos(rotation), np.sin(rotation)
    zoom = 2**-zoom / height

    x = np.arange(width, dtype='float64') + offset_x
    y = np.arange(height, dtype='float64') + offset_y

    x, y = np.meshgrid(x, y)

    x = (2 * x - width) * zoom
    y = (2 * y - height) * zoom

    x, y = x*c + y*s, y*c - x*s
    x += center_x
    y += center_y

    return x, y


def threaded_anti_alias(generate_subpixel_image, width, height, anti_aliasing, num_channels=3):
    lock = Lock()

    result = np.zeros((num_channels, height, width))

    def accumulate_subpixels(offset_x, offset_y):
        nonlocal result

        subpixel_image = generate_subpixel_image(offset_x, offset_y)

        lock.acquire()
        result += subpixel_image
        lock.release()

    ts = []
    offsets = np.arange(anti_aliasing) / anti_aliasing
    for i in offsets:
        for j in offsets:
            ts.append(Thread(target=accumulate_subpixels, args=(i, j)))
            ts[-1].start()
    for t in ts:
        t.join()

    result /= anti_aliasing**2

    return result
