import math
import random
from PIL import Image
WIDE = False
imgx = 4096
imgy = 4096
image = Image.new("RGB", (imgx, imgy), (0,0,0))
maxIt = 100000  # количество итераций
BASE = 3
s = math.sqrt(3.0)
def f(z):
    return BASE / ((BASE/3) + s - z) - ((BASE/3) + s) / ((BASE/3*2) + s)
ifs = ["f(z)", "f(z) * complex(-1.0, s) / 2.0", "f(z) * complex(-1.0, -s) / 2.0"]
xa = -0.6
xb = 0.9
ya = -0.75
yb = 0.75
z = complex(0.0, 0.0)
for i in range(maxIt):
    z = eval(ifs[random.randint(0, 2)])
    BASE = z**3.65
    kx = int((z.real - xa) / (xb - xa) * (imgx - 1))
    ky = int((z.imag - ya) / (yb - ya) * (imgy - 1))
    if kx >= 0 and kx < imgx and ky >= 0 and ky < imgy:
        image.putpixel((kx, ky), (255, 255, 255))
        try:
            if WIDE==True:1/0
            image.putpixel((kx-1,ky),(255,255,255))
            image.putpixel((kx+1,ky),(255,255,255))
            image.putpixel((kx,ky+1),(255,255,255))
            image.putpixel((kx,ky-1),(255,255,255))
            image.putpixel((kx-1,ky-1),(255,255,255))
            image.putpixel((kx-1,ky+1),(255,255,255))
            image.putpixel((kx+1,ky-1),(255,255,255))
            image.putpixel((kx+1,ky+1),(255,255,255))
        except:None
image.save("ApollonianGasket.png", "PNG")
