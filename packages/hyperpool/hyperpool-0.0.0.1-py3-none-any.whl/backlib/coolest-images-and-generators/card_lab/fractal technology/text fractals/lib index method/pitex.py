import os;import string

ITER = 1
WIDTH = 10

lib = list(string.ascii_uppercase+string.ascii_lowercase+string.digits+string.ascii_uppercase+string.ascii_lowercase+string.digits+string.ascii_uppercase+string.ascii_lowercase+string.digits+string.ascii_uppercase+string.ascii_lowercase+string.digits+string.ascii_uppercase+string.ascii_lowercase+string.digits+string.ascii_uppercase+string.ascii_lowercase+string.digits+string.ascii_uppercase+string.ascii_lowercase+string.digits+string.ascii_uppercase+string.ascii_lowercase+string.digits+string.ascii_uppercase+string.ascii_uppercase+string.ascii_lowercase+string.digits+string.ascii_uppercase+string.ascii_lowercase+string.digits+string.ascii_uppercase+string.ascii_lowercase+string.digits+string.ascii_uppercase+string.ascii_lowercase+string.digits+string.ascii_uppercase+string.ascii_lowercase+string.digits+string.ascii_uppercase+string.ascii_lowercase+string.digits+string.ascii_uppercase+string.ascii_lowercase+string.digits+string.ascii_uppercase+string.ascii_lowercase+string.digits+string.ascii_uppercase+string.ascii_lowercase+string.digits)
def char(x):
    return lib[x]
def getid(x):
    for i in range(10000):
        if chr(i)==x:return i
    return 0
def mand(x,y):
    a = complex(x,y)
    a0 = 0
    for i in range(ITER):
        if abs(a0)>500:return 500
        a0 = a0-((a**2+(x**1.5))-y)
    if abs(a0)>500:return 500
    else:return abs(a0)
def wrix(index):
    a = char(round(abs(round(abs(index)))))
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
