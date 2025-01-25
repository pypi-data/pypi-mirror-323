from PIL import Image
import numpy as np
def _mand(a,base):
    x = a[0]
    y = a[1]
    c0 = complex(x,y)
    c = 0
    for i in range(100):
        if abs(c)>2:
            return (255,255,255)
        c = c**base+c0
    return (0,0,0)
def mandelbrot(WIDTH,file='img.png',base=2):
    img = Image.new('RGB',(WIDTH,int(WIDTH/2)))
    pixels = img.load()
    for x in range(WIDTH):
        print(x/WIDTH*100)
        for y in range(int(WIDTH/2)):
            a = (
                (x-(0.75*WIDTH))/(WIDTH/4),
                (y-(WIDTH/4))/(WIDTH/4),
                )
            pixels[x,y]=_mand(a,base)
    img.save(file)
    img.show()
