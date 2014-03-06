#! /usr/bin/python3.3
import time
import tkinter as tk
import math
import pstats
import colorsys
import cProfile
import time
from numpy import *
from random import random

## Celestial body with numpy matrices position X, velocity V, and mass m.
class Body:
    def __init__(self, massFactor, canvas, X = zeros(2), V = zeros(2)):
        self.Exists = True
        self.X = X
        self.V = V
        self.mass = (massFactor*10)**11
        self.canvas = canvas
        self.updateRadius()
        ## Let the point take care of its oval, that way we can update positions rather than
        ## Recreate them all. NB: Tk is terrible for this type of thing.
        self.oval = canvas.create_oval(X[0] - self.r, X[1] - self.r,
                                       X[0] + self.r, X[1] + self.r,)
        self.updateColour(massFactor)


    ## sets the radius of each body relative to the cube root of its mass, scaled to be a reasonable size.
    def updateRadius(self):
        self.r = self.mass**(1/3) / 2000

    ## sets the colour for each point relative to its mass
    def updateColour(self, m):
        self.color =  colorsys.hls_to_rgb(m, 0.5, 1)
        r = self.color[0] * 255
        g = self.color[1] * 255
        b = self.color[2] * 255
        #Convert RGB to hex
        self.hex = '#%02x%02x%02x' % (r,g,b)
        self.canvas.itemconfig(self.oval, fill = self.hex, outline = self.hex)
        
    ## Redraw circle at coords self.X with radius self.r
    def redraw(self):
        self.canvas.coords(self.oval,self.X[0] - self.r, self.X[1] - self.r,
                           self.X[0] + self.r, self.X[1] + self.r)

## Field of celestial bodies, main integration and such should happen here.
class Field:
    G = 6.67E-11
    def __init__(self, numBodies, fieldSize, canvas):
        self.bodArr = [None] * numBodies
        ## Large central body.
        self.bodArr[-1] = (Body(1.3, canvas))
        ## Init arrays for vectorised integrator.
        self.posArr  = zeros([numBodies, 2])
        self.velArr  = zeros([numBodies, 2])
        self.massArr = zeros([numBodies, 2])
        ## Instantiate all but the last planet, this will be the sun.
        for i in range(len(self.bodArr) - 1):
            ## Random radius, angle, and mass. NB: Power is to skew mass distribution.
            r = random() * fieldSize
            a = random() * 2 * math.pi
            massFactor = random()

            ## Set random, position w/ uniform r distrib.
            X = self.polarToCart(r, a)
            ## Set V st body has approx energy needed for circular orbit.
            V = self.circOrbitVel(X, self.bodArr[-1].mass)
            
            self.bodArr[i] = Body(massFactor, canvas, X, V)


    ## Integrator using vector functions because I can't figure timestep operator.
    ## Leaves the OO data structure intact at the end.
    ## Presently does not merge bodies after a collision.
    def update(self):
        [pos,vel] = self.bod2Vectors(self.bodArr)
        ## Calculate accelerations for integrator.
        accel = self.calcAccel(pos, self.massArr)
        self.velVerletIntegrate(pos, vel, accel, 1)
        # Copy flat arrays back into objects.
        self.vec2Bodies(pos, vel, self.bodArr)

    ## Copy coordinates from bodies to vectors.
    def bod2Vectors(self, bodies):
        # Copy position velocity and mass data to flat arrays in O(n) time.
        for i in range(len(bodies)):
            self.posArr[i] = bodies[i].X
            self.velArr[i] = bodies[i].V
            self.massArr[i] = bodies[i].mass
        return [self.posArr,self.velArr]

    ## Copy coordinates from vectors to bodies.
    def vec2Bodies(self, pos, vel, bodies):
        for i in range(len(pos)):
            bodies[i].X = pos[i]
            bodies[i].V = vel[i]

    ## Euler integration 
    def eulerIntegrate(self, pos, vel, accel, dt):
        # O(n) update to velocity/position.
        vel += dt * accel
        pos += dt * vel
    def velVerletIntegrate(self, pos, vel, accel, dt):
        pos += vel * dt + (dt**2 / 2) * accel
        accel2 = self.calcAccel(pos, self.massArr)
        vel += 1/2 * (accel + accel2) * dt

    ## Calculate acceleration for field with bodies in [n,2] shape array pos
    ##  with masses in [n] shape array mass.
    def calcAccel(self, pos, mass):
        accel = zeros([len(pos),2])
        ## We calculate the force of each body on all the other bodies and
        ##  accumulate it.
        for i in range(len(pos)):
            ## Subtract position vector of body[i] from position of every other.
            displacement = pos - pos[i]
            ## Find an array of scalar distances squared.
            distance = sum(displacement**2, axis=1)

        
            ## Collision detection should use a numpy.where or similar here.


            ## Cap the minimum distance so we don't divide by 0.
            ## Also raise to %-1.5, because GmM / r^2 * rVec needs
            ##  has extra factor of r in magnitude of rVec
            distance = maximum(distance, 1E-10)**-1.5

            ## Finally calculate GM/r^3 * rVec.
            accel += -(displacement.T * distance).T * Field.G * mass[i]
        return accel
        
    ## Return numpy array containing cartesian coordinates x (out[0]) and y (out[1])
    ##  corresponding to radius r and angle a.
    def polarToCart(self, r, a):
        return array([r * math.cos(a), r * math.sin(a)])

    ## Return 2d velocity vector corresponding to orbit at position X and combined
    ##  mass Mass
    def circOrbitVel(self, X, Mass):
        r = linalg.norm(X)
        mag = (Field.G * Mass / r)**0.5 / r
        return array([-X[1] * mag,
                       X[0] * mag])
                    

## Draw and update function.
class Draw():
    def __init__(self, master,w = 600,h = 600):
        self.width = w
        self.height = h
        self.canvas = tk.Canvas(master, width = self.width, height = self.height, background = 'black')
        ##This sets what a 'unit' is in pixels.
        self.canvas.configure(xscrollincrement='1', yscrollincrement='1')
        self.canvas.xview_scroll(int(-w/2), "units")
        self.canvas.yview_scroll(int(-h/2), "units")
        self.canvas.pack(expand=True, fill=tk.BOTH)
        canvasRad = min(w,h)*0.4
        self.field = Field(300, canvasRad, self.canvas)
        
    def drawFrame(self):
        self.field.update()
        for body in self.field.bodArr:
            if body.Exists == True:
                body.redraw()
        self.canvas.update()
        time.sleep(1/60)

    def update(self, width, height):
        self.width = width
        self.height = height
        ## Put origin at 0,0 to keep screen coords out of simulation.
        ## As much as pos.
        self.canvas.xview_scroll(int(-self.width/2), "units")
        self.canvas.yview_scroll(int(-self.height/2), "units")
        self.canvas.pack()

class Application():
    def __init__(self):
        self.root = tk.Tk()
        self.d = Draw(self.root)
        self.i = 1
        self.width = self.root.winfo_width()
        self.height = self.root.winfo_height()
        self.root.bind('<Key>', self.reset)
        self.root.after(1, self.runSim)
        self.root.mainloop()
        #myFunction() # This is my function. It works.

    ## Run the simulation. Used in call-backs from tkinter.
    def runSim(self):
        while True:
            self.d.drawFrame()

    ## Used to reset the simulation (new simulation).
    def reset(self, event):
        if 'r' in repr(event.char):
            self.d.canvas.destroy()
            self.d = Draw(self.root, self.root.winfo_width(), self.root.winfo_height())

    def resize(self, event):
        self.d.update(event.width, event.height)

a = Application()
