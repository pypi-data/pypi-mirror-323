from generativepy.bitmap import Scaler
from generativepy.nparray import (make_nparray_data, make_npcolormap, save_nparray,
                                  load_nparray, save_nparray_image, apply_npcolormap)
from generativepy.color import Color
import numpy as np
import sys
import math
import cmath as cath
def folder():
    a = sys.argv[0]
    a=a.replace("clove.py","image.png")
    return a
MAX_COUNT = 120
WIDTH = 256
HEIGHT = 200
bas1 = 0.6
bas2 = 1.5
bas3 = 0.3
bas4 = 2
def calc(c1, c2):
    x = y = 0
    for i in range(MAX_COUNT):
        x, y = x**bas1 - y**bas2 + c1, abs((bas4*x*y)**bas3) + c2
        if abs(abs(x)**bas4) - abs(abs(y)**bas2) > 4:
            return i + 1
    return 0


def paint(image, pixel_width, pixel_height, frame_no, frame_count):
    scaler = Scaler(pixel_width, pixel_height, width=3.2, startx=-2, starty=-1.8)

    for px in range(pixel_width):
        print(px/pixel_width*100)
        for py in range(pixel_height):
            x, y = scaler.device_to_user(px, py)
            count = calc(x, y)
            image[py, px] = count


def colorise(counts):
    counts = np.reshape(counts, (counts.shape[0], counts.shape[1]))

    colormap = make_npcolormap(MAX_COUNT+2,
                               [Color('gray'), Color('white'), Color('purple'), Color('magenta')],# Color('lightpurple')],
                               [24, 48, 200])#, 128])

    outarray = np.zeros((counts.shape[0], counts.shape[1], 3), dtype=np.uint8)
    apply_npcolormap(outarray, counts, colormap)
    return outarray


data = make_nparray_data(paint, WIDTH, HEIGHT, channels=1)

save_nparray(folder(), data)
data = load_nparray(folder())

frame = colorise(data)

save_nparray_image('image.png', frame)
