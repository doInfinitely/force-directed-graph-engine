from sphere import sphere
import sys
import math

class particle(sphere):
    def __init__(self, key, pos, rad, vel, prd, chr, mss, c, IDer=None, bonds=None):
        sphere.__init__(self, key, pos, rad, vel)
        self.prd = prd #emit Freq
        self.chr = chr
        self.mss = mss
        self.c = c
        self.IDer = IDer
        self.emit = True
        self.bonds = bonds

    def action(self):
        #print 'action'
        if self.emit:
            self.emit = False
            return [[self.prd,'emit',[self.key]]]
        else:
            return []

    def emission(self):
        newF = force(self.IDer.getID(), [x for x in self.pos], [x for x in self.rad], [0 for x in self.vel], self.prd, self.chr, 1, self, self.bonds)
        #print newF.key
        self.contain[newF.key] = newF
        newF.parents[self.key] = self
        newF.engulf(self) #force carrier moves out of particle
        newF.rad = [sys.float_info.min, self.c]
        #newF.eventQ = self.action()

    def forced(self, forc):
        dist = self.euclidean(self.pos,forc.pos)
        if dist != 0:
            bondF = 0
            if forc.bonds != None:
                if frozenset([self.key,forc.mkr.key]) in forc.bonds:
                    bond = forc.bonds[frozenset([self.key,forc.mkr.key])]
                    if bond['type'] == 0: #spring
                        bondF = bond['k']*(bond['eqlen']-forc.rad[0])
                    elif bond['type'] == 1: #bungy
                        bondF = min(bond['k']*(bond['eqlen']-forc.rad[0]), 0)
                    elif bond['type'] == 2: #arm
                        bondF = max(bond['k']*(bond['eqlen']-forc.rad[0]), 0)
            for i in range(len(self.pos)):
                #dmv = forc.rad[1]*(self.pos[i]-forc.pos[i])/dist
                dmv = (self.pos[i]-forc.pos[i])/dist
                #dmv += forc.vel[i]
               	#mv = dmv-self.vel[i]
                #dmv *= math.copysign(1,forc.chr*self.chr)
                #print 'dmv', dmv, dmv*forc.chr/( max(forc.rad[0],1)**2)
                #print dmv
                #self.vel[i] += 10*dmv*forc.chr/( max(forc.rad[0],1)**2)*self.chr*(forc.mss-self.mss)

                self.vel[i] += 10*dmv*(forc.chr*self.chr/( max(forc.rad[0],0)**2)+bondF)*forc.prd/self.mss

            spd = self.euclidean(self.vel, [0 for z in range(len(self.vel))] )
            if spd >= self.c-1e-5:
                for i in range(len(self.vel)):
                    self.vel[i] *= (self.c-1e-5)/spd
            self.velChanged = True
            print self.key, 'forced', self.vel
            

    def engulfedBy(self, other):
        #print 'test'
        if isinstance(other, force):
            self.forced(other)

                

    def euclidean(self,v1,v2):
        return math.sqrt(sum([ (v1[i]-v2[i])**2 for i in range(len(v1)) ]))
class force(sphere):
    def __init__(self, key, pos, rad, vel, prd, chr, mss = 1, mkr=None, bonds=None):
        sphere.__init__(self, key, pos, rad, vel)
        self.prd = prd
        self.chr = chr
        self.mss = mss
        self.mkr = mkr
        self.bonds = bonds

    def engulfedBy(self, other):
        for x in self.contain:
            x.engulfedBy(other)

class IDer:
    def __init__(self):
        self.IDs = set()
    def getID(self):
        i = 0
        while i in self.IDs:
            i += 1
        self.IDs.add(i)
        return i

if __name__=="__main__":
    space = sphere(-1, [0,0], None, [0,0])
    ider = IDer()
    part = particle(ider.getID(), [0,2], [0,0], [0,0], .1, 1, 1, 1, ider)
    space.contain[part.key] = part
    part.parents[space.key] = space
    print part

    for i in range(6):
        space.internalCollision()
        print 'space','Event', [[x[0],x[1],[y.key for y in list(x[2])] ] for x in space.eventQ]
        try:
            print [[x[0],x[1],[y for y in list(x[2])] ] for x in [space.nextEvent()]]
            advance = space.nextEvent()[0]
            space.progress(advance)
            print part.eventQ
            space.execute()
        except TypeError:
            print None
        print ' '

    print space.contain
    print space.allSpheres()
