from PIL import Image
from numpy import complex64 as complex, array
import colorsys
from math import *
import cmath as s
class vector():
    x = 0
    y = 0
    z = 0
    def __repr__(vec):
        x = vec.x
        y = vec.y
        z = vec.z
        return f"{x}x,{y}y,{z}z"
    def __init__(vec,x,y=0,z=0):
        vec.x = x
        vec.y = y
        vec.z = z
# setting the width of the output image as 4096
# but thats actually hard to compute
WIDTH = 1024
ITER = 75
# a function to return a tuple of colors
# as integer value of rgb
def rgb_conv(i):
    color = 255 * array(colorsys.hsv_to_rgb(i / 255.0, 1.0, 0.5))
    #return tuple(color.astype(int))
    return (255,255,255)#белый фон
# function defining a mandelbrot
def mandelbrot(vec):
    x = vec.x
    y = vec.y
    z = vec.z
    c0 = complex(x, y)
    c1 = complex(-x, -y)
    c2 = complex(-z,z)
    c = 0
    for i in range(1, ITER):
        if abs(c) > 2:
            return rgb_conv(i)
        c = (c**s.tan(c) + c0**s.sin(-c0))
    return (0,0,0)

# creating the new image in RGB mode
img = Image.new('RGB', (WIDTH, int(WIDTH/2)))
pixels = img.load()

for x in range(img.size[0]):

    # displaying the progress as percentage
    print("%.2f %%" % (x / WIDTH * 100.0)) 
    for y in range(img.size[1]):
        a = vector((x - (0.75 * WIDTH)) / (WIDTH / 4),
                (y - (WIDTH / 4)) / (WIDTH / 4)
                   )
        pixels[x, y] = mandelbrot(a)
# to display the created fractal after 
# completing the given number of iterations
img.show()
