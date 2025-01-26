import numpy as np
from PIL import Image

import random
from random import choice
def choose(*x):
    a = random.randint(0,len(x)-1)
    return x[a]
ITER = 10
WIDTH = 256

GREENMOD = 2.5
BLUEMOD = 2

barn = [
    [.0, .0, .0, .16, .0, .0],
    [.85, .04, -.04, .85, 0, 1.6],
    [.20, -.26, .23, .22, .0, 1.6],
    [-.15, .28, .26, .24, .0, .44],
]
barns = [.01, .85, .07, .07]


def generate_fern(x,y):

    # generate `num_points` indexes from 0 to 3 according to the probability
    rx = 0
    ry = 0
    rz = 0
    coeff = {
            'a':choose(barn[0][0],barn[1][0],barn[2][0],barn[3][0]),
            'b':choose(barn[0][1],barn[1][1],barn[2][1],barn[3][1]),
            'c':choose(barn[0][2],barn[1][2],barn[2][2],barn[3][2]),
            'd':choose(barn[0][3],barn[1][3],barn[2][3],barn[3][3]),
            'e':choose(barn[0][4],barn[1][4],barn[2][4],barn[3][4]),
            'f':choose(barn[0][5],barn[1][5],barn[2][5],barn[3][5])
            }
    for i in range(ITER):
        rx += [coeff['a'] * x + coeff['b'] * y + coeff['e'], coeff['c'] * x + coeff['d'] * y + coeff['f']][0]
        rx /= 2
        ry += [coeff['a'] * x + coeff['b'] * y + coeff['e'], coeff['c'] * x + coeff['d'] * y + coeff['f']][1]
        ry /= 2
        r = [coeff['b'] * x + coeff['a'] * y + coeff['e'], coeff['c'] * x + coeff['d'] * y + coeff['f']]
        rz += r[0]+r[1]
        rz /= 2
    return [rx,ry,rz]

img = Image.new('RGB',(WIDTH*2,(WIDTH)))
pixels = img.load()

for x in range(img.size[0]):
    for y in range(img.size[1]):
        point = generate_fern(x,y)
        X = int(point[0])
        Y = int(point[1])
        Z = int(point[2])
        pixels[x,y]=(0,int((X+Y)/GREENMOD),int((Z+Z/2)/BLUEMOD))
img.show()
