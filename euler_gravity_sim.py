## This program implements a very basic 2D gravity sim using Euler methods.

import random
import time
import tkinter as tk
import math

G = 6.67 * (10**-11)

## Holds the mass, positition and velocity data of every body.
class Point:
    def __init__(self, xPos, yPos, xVel, yVel, mass, xScale, yScale):
        self.xPos = xPos
        self.yPos = yPos
        self.xVel = xVel
        self.yVel = yVel
        self.mass = mass
        self.xScale = xScale
        self.yScale = yScale

    ## Applies the velocity of the point to the points position to simulate movement.
    ## Could be moved into Field to unify the functions.
    def move(self):
        self.xPos += self.xVel
        self.yPos += self.yVel
        self.xPos = self.xPos % self.xScale
        self.yPos = self.yPos % self.yScale
        
## Contains all of the points in the system, and performs all attraction / acceleration calculations
class Field:
    
    ## Creates n random points in (x, y) range
    def __init__(self, numPoints, xScale, yScale):
        ## Create an empty array of the correct size. Stops the runtime having to move potentially very large arrays.
        self.pointArray = [None] * numPoints
        for i in range(numPoints):
            ## Set the array to have a collection of random points scatered in the center of the window.
            xRand = random.random()
            yRand = random.random()
            mRand = (random.random() * 10)**11
            mStar = 10**13
            xPos = (xScale * xRand / 2) + (xScale / 4)
            yPos = (yScale * yRand / 2) + (yScale / 4)
            r = math.hypot((xPos - xScale/2), (yPos - yScale/2))
            self.pointArray[i] = Point(xPos,
                                       yPos,
                                       (-(yPos - yScale/2)/r) * (G * mStar / r)**.5,
                                       ((xPos - xScale/2)/r) *(G * mStar / r)**.5,
                                       mRand,
                                       xScale,
                                       yScale)
        self.pointArray.append(Point(xScale / 2, yScale / 2, 0, 0, mStar, xScale, yScale))
            
    def update(self):
        ## Create a temp array that will be used to store the updated positions as we work on each point.
        workArray = self.pointArray[:]
        ## Loop over eivery point
        for i in range(len(self.pointArray)):
            ## Calculate values against every other point, but not for a point against itself.
            for j in range(len(self.pointArray)):
                if i == j:
                    pass
                else:
                    ## Calculate the distance between two points, how much force there is between them, and then the
                    ## resulting x and y velocities that need to be added to the point.
                    dist = Field.calcDist(self.pointArray[i].xPos, self.pointArray[i].yPos, self.pointArray[j].xPos, self.pointArray[j].yPos)
                    force = Field.calcForce(self.pointArray[i].mass, self.pointArray[j].mass, dist)
                    workArray[i].xVel += Field.calcAccl(self.pointArray[i].mass, force, dist, self.pointArray[i].xPos, self.pointArray[j].xPos)
                    workArray[i].yVel += Field.calcAccl(self.pointArray[i].mass, force, dist, self.pointArray[i].yPos, self.pointArray[j].yPos)
            ## Move the point once all of the forces have been applied to it.
            workArray[i].move()
        ## Make a deep copy of the temp array to the instance array so that it can be used for drawing and future iteration.
        self.pointArray = workArray[:]
        
    def calcDist(x1, y1, x2, y2):
        ## calculate the absolute differences of the points
        ## and then the distance between them using a^2 + b^2 = c^2
        return ((abs(x1 - x2)**2) + (abs(y1 - y2)**2))**0.5

    def calcForce(m1, m2, r):
    ##def calcForce(m1, m2, r, g = 0.0001):
        ## calculate the force betweem points using Newtonion Gravitation, returns 0 in case of errors such as divide by 0.
        try: 
            temp = G * ((m1 * m2)/(r**2))
        except:
            temp = 0
        return temp

    ## Calculate the acceleration of a point using Newtonion Mechanics, returns 0 in case of errors such as divide by 0.
    ## The acelleration is calculated in one plane, x or y, hence needing both positions of the points and the distance
    ## between them
    def calcAccl(m, f, r, x1, x2):
        try:
            temp = (((x2 - x1) / r) * f) / m
        except:
            temp = 0
        return temp
            
class Draw():
    ## Create the window and field.
    def __init__(self, master):
        self.width = 800
        self.height = 800
        self.field = Field(30, self.width, self.height)
        self.canvas = tk.Canvas(master, width = self.width, height = self.height)
        self.canvas.pack()

    ## For every point in the field, draw a circle at its co-ordinates.
    def drawFrame(self):
        for j in range(len(self.field.pointArray)):
            self.canvas.create_oval(self.field.pointArray[j].xPos,
                                         self.field.pointArray[j].yPos,
                                         self.field.pointArray[j].xPos+math.log(self.field.pointArray[j].mass)/5,
                                         self.field.pointArray[j].yPos+math.log(self.field.pointArray[j].mass)/5)
        ## Update the canvas, otherwise nothing will be visible because the TK will wait until the program is out of a function to update the GUI by default.
        self.field.update()

root = tk.Tk()
while True:
    d = Draw(root)
    for i in range(10000):
        d.canvas.delete('all')
        d.drawFrame()
        d.canvas.update()
        time.sleep(1/30)
    d.canvas.destroy()
