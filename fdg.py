import math
import random

class fdg:

    def __init__(self,k = 10**-3):
        self.k = k
        self.charges = set()
        self.edges = set()

    def motion(self,time, decay=0):
        for item in self.charges:
            item.motion(time, decay)
    def clrF(self):
        for item in self.charges:
            item.clrF()
    def internalF(self):
        items = [item for item in self.charges]
        self.clrF()
        for i in range(len(items)):
            for j in range(i+1,len(items)):
                items[i].interact(items[j],self.k)
        for x in self.edges:
            endpoints = [y for y in x]
            self.connectCharges(endpoints[0],endpoints[1],.5,75)
    def run(self,time):
        self.internalF()
        self.motion(time, decay=1)
    class pCharge:
        def __init__(self, charge=10000.0, mass=1.0, dim=3):
            self.charge = charge
            self.mass = mass
            self.dim = dim
            self.pos = [0.0 for i in range(self.dim)]
            self.vel = [0.0 for i in range(self.dim)]
            self.acc = [0.0 for i in range(self.dim)]
            self.anchored = False
        def appF(self,force):
            for i in range(min(len(force),self.dim)):
                self.acc[i] += force[i]/self.mass
        def clrF(self):
            self.acc = [0.0 for i in range(self.dim)]
        def movP(self,pos):
            for i in range(min(len(pos),self.dim)):
                self.pos[i] = pos[i]
        def pshP(self,vel):
            for i in range(min(len(vel),self.dim)):
                self.vel[i] = vel[i]
        def motion(self,time=1.0,decay=0):
            if self.anchored:
                for i in range(self.dim):
                    self.vel[i] = 0
            else: 
                for i in range(self.dim):
                    self.pos[i] += (self.vel[i]*time + self.acc[i]*time**2/2.0)#*(1-decay)
                    self.vel[i] += self.acc[i]*time
                    self.vel[i] *= (1.0-decay*.25)
        def interact(self, other, k):
            dist = 0.0
            for i in range(min(len(self.pos),len(other.pos))):
                dist += (other.pos[i]-self.pos[i])**2
            dist = dist**0.5
            mag = -1*k*self.charge*other.charge/dist**2
            force = []
            for i in range(min(len(self.pos),len(other.pos))):
                force.append( (other.pos[i]-self.pos[i])/dist*mag )
            self.appF(force)
            other.appF([-1*x for x in force])
        def spawnCharge(self,radius, charge=10000.0, mass=1.0):
            newC = fdg.pCharge(charge,mass,self.dim)
            if self.dim == 1:
                newC.pos[0] = radius*random.choice([-1,1])
                return newC
            angles = [random.random()*math.pi for i in range(self.dim-1)]
            pos2 = []
            while len(pos2) < newC.dim:
                r2 = radius**2
                for x2 in pos2:
                    r2 -= x2
                coeff = 1
                for i in range(newC.dim-len(pos2)-1):
                    coeff += coeff*math.tan(angles[i])**2
                pos2.append(r2/coeff)
            newC.pos = [self.pos[i]+pos2[i]**0.5*random.choice([-1,1]) for i in range(len(pos2))]
            print newC.pos
            return newC
    def spring(self, k,eqlen, start, end, bev=0):
        length = 0
        for i in range(min(len(start),len(end))):
            length += (end[i]-start[i])**2
        length = length**0.5
        mag = k*(length-eqlen)
        if length < eqlen and bev == 0:
            mag = 0
        force = []
        for i in range(min(len(start),len(end))):
            force.append( (end[i]-start[i])/length*mag ) 
        return (force,[-1*x for x in force])

    def connectCharges(self, charge0, charge1, k, eqlen):
        forces = self.spring(k,eqlen,charge0.pos,charge1.pos,1)
        charge0.appF(forces[0])
        charge1.appF(forces[1])
