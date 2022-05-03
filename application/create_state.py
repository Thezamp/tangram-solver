import random
from time import sleep
from turtle import Turtle, Screen

from PIL import ImageGrab

A = 198.0
a = A / 4.0
d = a * 2 ** .5

class TStein(Turtle):
    def __init__(self, size, name, shape="arrow", clickable=True):
        Turtle.__init__(self)
        self.name = name
        self.size = size
        self.pu()
        self.shape(shape)
        self.resizemode("user")
        self.turtlesize(size, size, 3)
        self.clicktime = -1

    def place(self, x, y, h):
        self.goto(x, y)
        self.setheading(h)

class TRhomboid(TStein):
    def __init__(self, name, clickable=True):
        TStein.__init__(self, 1, name, shape="rhomboid1", clickable=clickable)
        self.flipped = False
        self.pu()

    def flip(self):
        if not self.flipped:
            self.shape("rhomboid2")
            self.flipped = True
        else:
            self.shape("rhomboid1")
            self.flipped = False

def makerhomboidshapes(screen,designer):
    designer.shape("square")
    designer.shapesize(5, 2.5)
    designer.shearfactor(-1)  # needs Python 3.1
    designer.tilt(90)
    screen.register_shape("rhomboid1", designer.get_shapepoly())
    designer.shearfactor(1)
    screen.register_shape("rhomboid2", designer.get_shapepoly())






def setTiles(screen, data, STiles, TTiles):
    c1, c2, c3 = random.random() / 2, random.random() / 2, random.random() / 2
    arrangeTiles(data, TTiles)
    if TTiles[6].flipped:
        TTiles[6].flip()
    if STiles[6].flipped:
        STiles[6].flip()
    for i in range(7):
        TTiles[i].pencolor(c1, c2, c3)
        TTiles[i].fillcolor(c1 + random.random() / 2, c2 + random.random() / 2, c3 + random.random() / 2)
    #screen.update()

def arrangeTiles(data, tileset):
    flip = data[-1] == -1
    l = data[:7]
    for i in range(7):
        x, y, h = data[i]
        if i == 6 and flip:
            tileset[6].flip()
        tileset[i].place(x, y, h)

def dump_gui(canvas,w=800,h=600, name="puzzle_state.png"):
    x0 = canvas.winfo_rootx()
    y0 = canvas.winfo_rooty()
    x1 = x0 + w  # careful with the extractor
    y1 = y0 + h
    ImageGrab.grab().crop((x0, y0, x1, y1)).save(name)

def setpos(position, solution):
    xcoord= 800
    ycoord= 600
    screen = Screen()
    screen.setup(xcoord,ycoord)
    screen.tracer(False)
    screen.mode("logo")
    designer= Turtle(visible=False)
    designer.pu()
    canvas = screen.getcanvas()
    makerhomboidshapes(screen,designer)
    screen.bgcolor("gray10")
    STiles= [TStein(A / 20., "big triangle 1", clickable=False),
                  TStein(A / 20., "big triangle 2", clickable=False),
                  TStein(2 * d / 20., "middle triangle", clickable=False),
                  TStein(A / 40., "small triangle 1", clickable=False),
                  TStein(A / 40., "small triangle 2", clickable=False),
                  TStein(d / 20., "square", "square", clickable=False),
                  TRhomboid("parallelogram", clickable=False)]
    TTiles = [TStein(A / 20., "big triangle 1", clickable=False),
                  TStein(A / 20., "big triangle 2", clickable=False),
                  TStein(2 * d / 20., "middle triangle", clickable=False),
                  TStein(A / 40., "small triangle 1", clickable=False),
                  TStein(A / 40., "small triangle 2", clickable=False),
                  TStein(d / 20., "square", "square", clickable=False),
                  TRhomboid("parallelogram", clickable=False)]
    for s in STiles:
        s.color((1, 1, 0.9))
        s.turtlesize(s.size, s.size, 2)
        s.ht()

    #screen.update()
    setTiles(screen, position, STiles, TTiles)
    arrangeTiles(solution, STiles)

    for t in TTiles + STiles: t.showturtle()
    screen.update()
    sleep(0.2)
    dump_gui(canvas)
    #screen.bye()