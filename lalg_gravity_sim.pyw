#! /usr/bin/python3.3
import time
import tkinter as tk
import math
import numpy # Numpy 1.8
import pstats
import colorsys
import cProfile

## Keeping the namespace reasonably tidy for now.
## probably wise to do from numpy import * at some point.
from numpy import array
from random import random

## Celestial body with numpy matrices position X, velocity V, and mass m.
class Body:
    def __init__(self, X, V, m, canvas):
        self.Exists = True
        self.X = X
        self.V = V
        self.tempForce = array([0.,0.])
        self.mass = m
        self.canvas = canvas
        self.updateRadius()
        self.updateColour()
        ## Let the point take care of its oval, that way we can update positions rather than
        ## Recreate them all. NB: Tk is terrible for this type of thing.
        self.oval = canvas.create_oval(X[0] - self.r, X[1] - self.r,
                                       X[0] + self.r, X[1] + self.r,
                                       fill = self.hex,
                                       outline = self.hex)

    def updateRadius(self):
        self.r = self.mass**(1/3) / 2000

    def updateColour(self):
        self.color =  colorsys.hls_to_rgb(255 * self.mass, 128, 1)
        #Convert RGB to hex
        self.hex = '#%02x%02x%02x' % self.color
        
    ## Redraw circle at coords self.X with radius self.r
    def redraw(self):
        self.canvas.coords(self.oval,self.X[0] - self.r, self.X[1] - self.r,
                           self.X[0] + self.r, self.X[1] + self.r)

## Field of celestial bodies, main integration and such should happen here.
class Field:
    G = 6.67E-11
    sunMass = 1E12
    def __init__(self, numBodies, canvas):
        self.bodArr = [None] * numBodies
        ## Instantiate all but the last planet, this will be the sun.
        for i in range(len(self.bodArr) - 1):
            ## Random radius, angle, and mass. NB: Power is to skew mass distribution.
            r = random() * 150
            a = random() * 2 * math.pi
            m = (random()*10)**11
            
            X = self.polarToCart(r, a, array([0., 0.]))
            V = self.circOrbitVel(X,
                                  Field.sunMass + m,
                                  array([0., 0.]))
            self.bodArr[i] = Body(X, V, m, canvas)
            ## Don't forget to make EVERYTHING a float, or you're going to have a bad time.

        ## Large central body.
        self.bodArr[-1] = (Body(array([0., 0.]), array([0., 0.]), Field.sunMass, canvas))

    ## Integrator, still euler with the loop in the python. Now with added overhead!
    def update(self):

        G = Field.G
        norm = numpy.linalg.norm
        disp = array([0.,0.])
        for body in self.bodArr:
            if body.Exists == True:
                body.tempForce = array([0.,0.])
                GM = G * body.mass              #Hoist G*M1 calculation.
                for other in self.bodArr:
                    if other.Exists == False:
                        pass
                    elif not (body == other):
                        ## Find displacement without creating new array.
                        numpy.subtract(body.X, other.X, disp)
                        dist = norm(disp)
                        if dist <= body.r:
                            cMass = body.mass + other.mass
                            body.X = ((body.X * body.mass) + (other.X * other.mass)) / cMass
                            body.V = ((body.V * body.mass) + (other.V * other.mass)) / cMass
                            body.mass = cMass
                            other.Exists = False
                            other.canvas.delete(other.oval)
                            body.updateRadius()
                            body.updateColour()
                        else:
                            ## Multiply GMm/r**2 by disp vector / r then add in place to tempForce.
                            numpy.add(body.tempForce,
                                      numpy.multiply((-GM * other.mass) / (max(norm(disp),0.1)**3), (disp),disp),
                                      body.tempForce)
        for body in self.bodArr:
            if body.Exists == True:
                ## dV/dt = F/m
                body.V += body.tempForce / body.mass
                ## dX/dt = V
                body.X += body.V
            
    ## Return numpy array containing cartesian coordinates x (out[0]) and y (out[1]) corresponding to radius r and angle a.
    ## Supposed to have an optional out parameter so array can be edited in place.
    def polarToCart(self, r, a, out = array([0., 0.])):
        out[0] = r * math.cos(a)
        out[1] = r * math.sin(a)
        return out
    ## Return 2d velocity vector corresponding to orbit at position X and combined mass Mass
    def circOrbitVel(self, X, Mass, out = array([0., 0.])):
        r = numpy.linalg.norm(X)
        out[0] = -X[1]/r * (Field.G*Mass/r)**.5
        out[1] =  X[0]/r * (Field.G*Mass/r)**.5
        return out
                    

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
        self.field = Field(60, self.canvas)
    def drawFrame(self):
        self.field.update()
        for body in self.field.bodArr:
            if body.Exists == True:
                body.redraw()
        self.canvas.update()
        time.sleep(1/60)
def mainLoop():
    root = tk.Tk()
    d = Draw(root)
    i = 5000
    while i > 0:
        i -= 1
        d.drawFrame()

cProfile.run('mainLoop()', 'restats')
p = pstats.Stats('restats')
p.sort_stats('tottime')
p.print_stats(15)

