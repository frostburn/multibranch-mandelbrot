import argparse
from threading import Thread, Lock
import imageio
import progressbar
from pylab import *
from coloring import red_lavender, subharmonics
from mandelbrot import mandelbrot


RESOLUTIONS = {
    "2160p": (3840, 2160),
    "1440p": (2560, 1440),
    "1080p": (1920, 1080),
    "720p": (1280, 720),
    "480p": (854, 480),
    "360p": (640, 360),
    "240p": (426, 240),
    "160p": (284, 160),
    "80p": (142, 80),
    "40p": (71, 40),
}


def make_video_frame(rgb, indexing='ij', dither=1.0/256.0):
    if dither:
        rgb = [channel + random(channel.shape)*dither for channel in rgb]
    if indexing == 'ij':
        rgb = [channel.T for channel in rgb]
    frame = stack(rgb, axis=-1)
    frame = clip(frame, 0.0, 1.0)
    return (frame * 255).astype('uint8')


def do_render(args, writer):
    inside_cutoff = 2**9
    color_map = subharmonics
    for n in progressbar.progressbar(range(args.num_frames)):
        t = n / (args.num_frames - 1)
        x, y = -0.11042608495193805, -1.2321253969758166
        zoom = t * 44 - 2

        image = mandelbrot(args.width, args.height, x, y, zoom, 2.5, 66, color_map=color_map, anti_aliasing=args.anti_aliasing, inside_cutoff=inside_cutoff, clip_outside=True)

        frame = make_video_frame(image, indexing=None)
        writer.append_data(frame)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Render video frames of a Multi-branch Mandelbrot fractal')
    parser.add_argument('outfile', type=str, help='Output file name')
    parser.add_argument('--anti-aliasing', type=int, help='Anti-aliasing pixel subdivisions')
    parser.add_argument('--resolution', choices=RESOLUTIONS.keys(), help='Video and simulation grid resolution')
    parser.add_argument('--width', type=int, help='Video and simulation grid width', metavar='W')
    parser.add_argument('--height', type=int, help='Video and simulation grid height', metavar='H')
    parser.add_argument('--framerate', type=int, help='Video frame rate')
    parser.add_argument('--video-quality', type=int, help='Video quality factor')
    parser.add_argument('--video-duration', type=float, help='Duration of video to render in seconds')
    args = parser.parse_args()

    if not args.anti_aliasing:
        args.anti_aliasing = 2
    if not args.framerate:
        args.framerate = 24
    if not args.video_quality:
        args.video_quality = 10

    writer = imageio.get_writer(args.outfile, fps=args.framerate, quality=args.video_quality, macro_block_size=1)

    # Compute derived parameters
    if args.resolution:
        width, height = RESOLUTIONS[args.resolution]
        if not args.width:
            args.width = width
        if not args.height:
            args.height = height
    if (not args.width) or (not args.height):
        raise ValueError("Invalid or missing resolution")
    if not args.video_duration:
        raise ValueError("Missing video duration")
    args.aspect = args.width / args.height
    args.num_frames = int(args.video_duration * args.framerate)
    args.dt = 1.0 / args.num_frames

    do_render(args, writer)

    writer.close()
