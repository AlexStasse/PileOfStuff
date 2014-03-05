import time
import tkinter as tk
import math
import numpy
## Keeping the namespace reasonably tidy for now.
## probably wise to do from numpy import * at some point.
from numpy import matrix
from random import random

## Celestial body with numpy matrices position X, velocity V, and mass m.
class Body:
    def __init__(self, X, V, m, canvas):
        self.X = matrix(X)
        self.V = matrix(V)
        self.tempForce = matrix([0.,0.])
        self.mass = m
        self.canvas = canvas
        self.r = m**(1/3) / 2000
        ## Let the point take care of its oval, that way we can update positions rather than
        ## Recreate them all. NB: Tk is terrible for this type of thing.
        self.oval = canvas.create_oval(self.X.A1[0] - self.r, self.X.A1[1] - self.r,
                         self.X.A1[0] + self.r, self.X.A1[1] + self.r,
                        fill = 'white',
                        outline = 'white')
    def redraw(self):
        self.canvas.coords(self.oval,self.X.A1[0] - self.r, self.X.A1[1] - self.r,
                         self.X.A1[0] + self.r, self.X.A1[1] + self.r)

## Field of celestial bodies, main integration and such should happen here.
class Field:
    G = 6.67E-11
    def __init__(self, numBodies, canvas):
        self.bodArr = [None] * numBodies
        for i in range(len(self.bodArr)):
            #x = random() - 0.5
            #y = random() - 0.5
            r = random()*150
            a = random() * 2 * math.pi
            x = r * math.cos(a)
            y = r * math.sin(a)
            m = (random()*10)**11
            xv = -y/r * (Field.G*(1E12+m)/r)**.5
            yv =  x/r * (Field.G*(1E12+m)/r)**.5
            self.bodArr[i] = Body(matrix([x,y]),matrix([xv,yv]),m, canvas)
        ## Don't forget to make EVERYTHING a float, or you're going to have a bad time.

        ## Large central body.
        self.bodArr[0].X = matrix([0.,0.])
        self.bodArr[0].V = matrix([0.,0.])
        self.bodArr[0].mass = float(1E12)
        self.bodArr[0].r = self.bodArr[0].mass**(1/3) / 2000

    ## Integrator, still euler with the loop in the python. Now with added overhead!
    def update(self):
        for body in self.bodArr:
            body.tempForce = matrix([0.,0.])
            for other in self.bodArr:
                if not (body == other):
                    ## GMm/r**2 for each other body
                    body.tempForce += (Field.G * body.mass * other.mass) * (numpy.linalg.norm(body.X - other.X)**-3 * -(body.X - other.X))
        for body in self.bodArr:
            ## dV/dt = F/m
            body.V += body.tempForce / body.mass
            ## dX/dt = V
            body.X += body.V

## Draw and update function.
class Draw():
    def __init__(self, master,w = 600,h = 600):
        self.width = w
        self.height = h
        self.canvas = tk.Canvas(master, width = self.width, height = self.height, background = 'black')
        ##This sets what a 'unit' is in pixels, though you could use 2i for 2 inches or 5mm for 5 millimetres
        ##the default was something retarded like 1/10th of a mm I dunno
        self.canvas.configure(xscrollincrement='1', yscrollincrement='1')
        self.canvas.xview_scroll(int(-w/2), "units")
        self.canvas.yview_scroll(int(-h/2), "units")
        self.canvas.pack()
        self.field = Field(40, self.canvas)
    def drawFrame(self):
        self.field.update()
        for body in self.field.bodArr:
            body.redraw()
        self.canvas.update()
        time.sleep(1/30)

root = tk.Tk()
d = Draw(root)
while True:
    d.drawFrame()
