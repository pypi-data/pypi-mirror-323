from tkinter import *  # Python 3
#from Tkinter import *  # Python 2
import turtle as tr
from svg_turtle import SvgTurtle
from PIL import Image
import os
import cairosvg as cairo
WIDTH = 16
HEIGHT = (WIDTH//5)*4
def save():
    t = SvgTurtle(0,0)
    t.save_as('foo.svg')
    #code svg to png
      
    # creating a SVG surface 
    # here geek is file name & 700, 700 is dimension 
    with cairo.SVGSurface('foo.svg', WIDTH, HEIGHT) as surface: 
      
        # creating a cairo context object 
        context = cairo.Context(surface) 
        # Save as a SVG and PNG
        context.fillcolor('red')
        context.beginfill()
        context.teleport(30,30)
        context.goto(-30,30)
        context.goto(-30,-30)
        context.goto(30,-30)
        context.goto(30,30)
        context.endfill()
        surface.write_to_png('image.png') 
      
    #/code svg to png
    os.remove('foo.svg') # optional
turtle = SvgTurtle(WIDTH,HEIGHT)
#draw

#/draw
save()
