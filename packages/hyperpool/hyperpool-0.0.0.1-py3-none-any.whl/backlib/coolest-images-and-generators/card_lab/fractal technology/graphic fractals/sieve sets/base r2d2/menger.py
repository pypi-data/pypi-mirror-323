from PIL import Image
from numpy import complex64 as complex, array
import colorsys
from random import randint as r
from math import sin,tan
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
# but thats actually easy to compute
WIDTH = 1024
# a function to return a tuple of colors
# as integer value of rgb
def rgb_conv(i):
    #color = 255 * array(colorsys.hsv_to_rgb(i / 255.0, 1.0, 0.5))
    #return tuple(color.astype(int))
    return (255,255,255)#белый фон
# function defining a mandelbrot
#010
#010
#010

#000
#111
#000
def d(x):
    a = r(0,round(sin(r(0,r(round(sin(x)),round(sin(x)+tan(x))))))+1)
    return a
def mandelbrot(vec):
    x = vec.x
    y = vec.y
    if x <=1:x=1
    if x >=2:x=1
    rnd = r(0,x)
    ans = int(int(rnd+d(x))/2)
    if ans > 1:return (ans*64,ans*64,ans*64)
    if ans == 1:return (255,255,255)
    if ans < 1 and ans>0:return (int(255/ans),int(255,ans),int(255,ans))
    return (0,0,0)

# creating the new image in RGB mode
img = Image.new('RGB', (WIDTH, int(WIDTH/2)))
pixels = img.load()

for x in range(img.size[0]):

    # displaying the progress as percentage
    print("%.2f %%" % (x / WIDTH * 100.0)) 
    for y in range(img.size[1]):
        a = vector(x,y)
        pixels[x, y] = mandelbrot(a)
# to display the created fractal after 
# completing the given number of iterations
img.show()
