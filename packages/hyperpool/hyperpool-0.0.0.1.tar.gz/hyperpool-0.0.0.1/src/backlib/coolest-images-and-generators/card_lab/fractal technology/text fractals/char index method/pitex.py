import os

ITER = 5
WIDTH = 200
def getid(x):
    for i in range(10000):
        if chr(i)==x:return i
    return 0
def mand(x,y):
    a = complex(x,y)
    a0 = 0
    for i in range(ITER):
        if abs(a0)>3000:return 3000
        a0 = a0-((a**2+(x**1.5))-y)
    return a0
def wrix(index):
    a = chr(round(abs(round(abs(index)))))
    b = open("test","w+")
    try:
        b.write(a)
        b.close()
        wrx = True
    except:
        wrx = False
    b.close()
    if wrx:
        b = open("text.txt","a+")
        b.write(a)
        b.close()
    os.remove('test')
a = open("text.txt","w+")
a.close()
for x in range(WIDTH):
    print(x/WIDTH*100)
    for y in range(WIDTH):
        wrix(mand(x,y))
