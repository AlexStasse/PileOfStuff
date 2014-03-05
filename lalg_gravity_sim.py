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
        ## Let the point take care of its oval, that way we can update positions rather than
        ## Recreate them all. NB: Tk is terrible for this type of thing.
        self.oval = canvas.create_oval(self.X.A1[0] - 1, self.X.A1[1] - 1,
                         self.X.A1[0] + 1, self.X.A1[1] + 1,
                        fill = 'white',
                        outline = 'white')
    def redraw(self):
        self.canvas.coords(self.oval,self.X.A1[0] - 1, self.X.A1[1] - 1,
                         self.X.A1[0] + 1, self.X.A1[1] + 1)

## Field of celestial bodies, main integration and such should happen here.
class Field:
    G = 6.67E-11
    def __init__(self, numBodies, canvas):
        self.bodArr = [None] * numBodies
        for i in range(len(self.bodArr)):
            x = random() - 0.5
            y = random() - 0.5
            self.bodArr[i] = Body(matrix([x,y])*400,matrix([0.,0.]),random()*1E8, canvas)
        ## Don't forget to make EVERYTHING a float, or you're going to have a bad time.

        ## Large central body.
        self.bodArr[0].X = matrix([0.,0.])
        self.bodArr[0].V = matrix([0.,0.])
        self.bodArr[0].mass = 1.1 * 1E12

    ## Integrator, still euler with the loop in the python. Now with added overhead!
    def update(self):
        disp = matrix([0,0])
        G = Field.G
        norm = numpy.linalg.norm
        for body in self.bodArr:
            body.tempForce = matrix([0.,0.])
            GM = G * body.mass
            for other in self.bodArr:
                if not (body == other):
                    disp = body.X - other.X
                    ## GMm/r**2 for each other body
                    body.tempForce += (-GM * other.mass) * (norm(disp)**-2) * (disp)
        for body in self.bodArr:
            ## dV/dt = F/m
            body.V += body.tempForce / body.mass
            ## dX/dt = V
            body.X += body.V

## Draw and update function.
class Draw():
    def __init__(self, master,w = 800,h = 800):
        self.width = w
        self.height = h
        self.canvas = tk.Canvas(master, width = self.width, height = self.height, background = 'black')
        ## Can't for the life of me figure out what a 'unit' is. Something a bit less than a pixel.
        ## This at least puts the origin in the middle somewhere.
        self.canvas.xview_scroll(w*2, "units")
        self.canvas.yview_scroll(h*2, "units")
        self.canvas.pack()
        self.field = Field(20, self.canvas)
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
