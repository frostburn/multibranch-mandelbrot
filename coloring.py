from pylab import *


def red_lavender(inside, outside, inside_cutoff):
    outside = array([
        0.1 + 0.2*sin(0.3*outside + 3) + 0.3 + 0.3*cos(0.01923*outside - 43),
        0.1 + 0.2*cos(0.12*outside + 2.2) + 0.2 + 0.3*sin(0.0313238*outside + 0.12),
        0.1 + 0.3*sin(0.232*outside + 1) + 0.4 + 0.4*cos(0.009328*outside - 1) + 0.125*cos(0.523*outside+7)**3
    ]) * (inside == 0)
    outside[1] = minimum(*outside)-0.15
    outside[2] *= 1.5

    outside *= 1.1
    outside = clip(outside, 0, 1)**1.6

    if inside_cutoff:
        envelope = ((1 - inside / inside_cutoff))*(inside > 0)
    else:
        envelope = 1
    inside = array([
        0.1 + 0.1*cos(inside*0.05) + 0.4 + 0.4*sin(inside*0.01),
        0.1 + 0.1*sin(inside*0.32312) + 0.2 + 0.4*sin(inside*0.01123) + 0.2*cos(0.3212-1)**5,
        0.1 + 0.1*cos(inside*0.9434+1) + 0.3 + 0.4*cos(inside*0.01643-1)
    ]) * envelope
    inside *= 1.5
    inside = clip(inside, 0, 1)
    return inside + outside


def subharmonics(inside, outside, inside_cutoff):
    outside = 0.5 + 0.5 * array([sin(outside), sin(outside/2), sin(outside/3)])
    inside = log(inside+1)
    inside = (0.5 + 0.5 * array([cos(inside), cos(inside/2), cos(inside/3)])) * (inside > 0)
    return inside + outside

def black_multi_edge(inside, outside, inside_cutoff):
    return array([outside, outside, outside])**0.2


def rainbow(r, phase, _):
    return array([r * (1 + sin(phase)), r * (1 + sin(phase + 2*pi/3)), r * (1 + sin(phase + 3*pi/3))]) * 0.01


def gray(r, phase, _):
    return array([r, r, r]) * 1.1


def sepia(inside, outside, inside_cutoff):
    bg = array([0.99 + 0.001*outside, 0.95 + 0.0001*outside, 0.9 + 0.0001*outside])

    inside = (array([inside, inside, inside]) * 0.0005)**0.1

    return bg - inside
