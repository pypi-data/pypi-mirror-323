from scipy.io import wavfile
import numpy
import cmath
def emptylist(len):
    list = []
    for i in range(len):
        list.append(numpy.int16(0))
    return list
def empty(len):
    a = numpy.array(emptylist(len))
    return a
lenght = 1000#seconds just like WIDTH in fractals
samplerate = 2000
ITER = 20
def limit(x):
    x = abs(x)
    if x > 32100:x=32100
    if x < -32100:x=-32100
    return x
"""
def notes(data):
    assets = []
    musics = []
    for i in range(1,len(data)):
        assets.append(data[i-1])
        assets.append(data[i])
        musics.append(assets[i-1])
        musics.append(assets[i])
    return musics
"""
def proccess(x,y):
    a = 0
    a0 = complex(x,y)
    for i in range(1,ITER):
        a = cmath.cos(cmath.cos(x)+cmath.cos(y))+cmath.cos(a)
    return limit(a*100)
notes = empty(lenght)
for x in range(lenght):
    print(x/lenght*100)
    for y in range(lenght):
        notes[x] = proccess(x,y)
data = notes
wavfile.write(filename='audio.wav',rate=samplerate,data=data)
