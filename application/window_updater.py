import sys
import time, random
import tkinter
from turtle import Turtle, Screen, Vec2D
from PIL import ImageGrab

x_coordinate = 800
y_coordinate = 600

sys.setrecursionlimit(20000)
screen = Screen()
screen.setup(x_coordinate, y_coordinate)

screen.tracer(False)
screen.mode("logo")
designer = Turtle(visible=False)
designer.pu()

canvas = screen.getcanvas()

A = 198.0
a = A / 4.0
d = a * 2 ** .5


def dump_gui():
    """
    takes a png screenshot of a tkinter window, and saves it on in cwd
    """
    print('...dumping gui window to png')

    x0 = canvas.winfo_rootx()
    y0 = canvas.winfo_rooty()
    x1 = x0 + 800
    y1 = y0 + 600
    ImageGrab.grab().crop((x0, y0, x1, y1)).save("gui_image_grabbed.png")


def makerhomboidshapes():
    designer.shape("square")
    designer.shapesize(5, 2.5)
    designer.shearfactor(-1)  # needs Python 3.1
    designer.tilt(90)
    screen.register_shape("rhomboid1", designer.get_shapepoly())
    designer.shearfactor(1)
    screen.register_shape("rhomboid2", designer.get_shapepoly())


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
        screen.update()


def init():
    makerhomboidshapes()
    screen.bgcolor("gray10")
    STiles = [TStein(A / 20., "big triangle 1", clickable=False),
              TStein(A / 20., "big triangle 2", clickable=False),
              TStein(2 * d / 20., "middle triangle", clickable=False),
              TStein(A / 40., "small triangle 1", clickable=False),
              TStein(A / 40., "small triangle 2", clickable=False),
              TStein(d / 20., "square", "square", clickable=False),
              TRhomboid("parallelogram", clickable=False)]
    TTiles = [TStein(A / 20., "big triangle 1"),
              TStein(A / 20., "big triangle 2"),
              TStein(2 * d / 20., "middle triangle"),
              TStein(A / 40., "small triangle 1"),
              TStein(A / 40., "small triangle 2"),
              TStein(d / 20., "square", "square"),
              TRhomboid("parallelogram")]

    for s in STiles:
        s.color((1, 1, 0.9))
        s.turtlesize(s.size, s.size, 2)
        s.ht()

    screen.update()
    return STiles, TTiles


def setTiles(data, STiles, TTiles):
    c1, c2, c3 = random.random() / 2, random.random() / 2, random.random() / 2
    arrangeTiles(data, TTiles)
    if TTiles[6].flipped:
        TTiles[6].flip()
    if STiles[6].flipped:
        STiles[6].flip()
    for i in range(7):
        TTiles[i].pencolor(c1, c2, c3)
        TTiles[i].fillcolor(c1 + random.random() / 2, c2 + random.random() / 2, c3 + random.random() / 2)
    screen.update()


def arrangeTiles(data, tileset):
    flip = data[-1] == -1
    l = data[:7]
    for i in range(7):
        x, y, h = data[i]
        if i == 6 and flip:
            tileset[6].flip()
        tileset[i].place(x, y, h)


def setgame(startdata,solution, STiles, TTiles):
    global Counter, tangram_solution_1, tangram_solutions, tangram_puzzle_idx

    Counter = 0

    setTiles(startdata, STiles, TTiles)
    arrangeTiles(solution, STiles)

    for t in TTiles + STiles: t.showturtle()
    screen.update()


def main(position,solution):
    STiles, Ttiles = init()

    setgame(position,solution, STiles, Ttiles)
    time.sleep(0.1)
    dump_gui()

    time.sleep(1)

    setgame([(250, 99, 90), (349, 0, 270), (200, -49, 225), (151, 49, 90), (250, -49, 0), (200, 0, 45),
                 (0, -74, 90), -1], solution, STiles,Ttiles)

    screen.exitonclick()
    #screen.mainloop()


if __name__ == '__main__':
    position = [(250, 99, 180), (349, 0, 270), (200, -49, 225), (151, 49, 90), (250, -49, 0), (200, 0, 45),
                 (274, -74, 90), 1]
    solution = [(-131, -43, 45), (-131, 99, 135), (-112, -63, 225), (-140, -152, 135), (-65, 244, 0), (-65, 207, 0),
                (-192, 90, 90), -1]
    main(position,solution)
