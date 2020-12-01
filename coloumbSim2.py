import particleTracker
import math

class tcpParticleSim:
    def __init(self):
        #refresh rate
        self.rr = .2

        #force rate
        self.fr = .1
        
        #rate of force expansion
        self.c = 1

        self.t = 0

        self.eventQ = []
        self.create = []
        self.erase = set()
        self.points = dict()
        self.coll = dict()
        self.mask = set()
        self.IDs = set()


        self.eventQ.append([0,'refresh',None])
        i = 0
        while i < len(self.eventQ) and self.eventQ[i][0] <= self.t+self.rr:
            i += 1
        self.eventQ.insert(i, [self.t+self.rr,'refresh',None])

        i = 0
        while i < len(self.eventQ) and self.eventQ[i][0] <= self.t+self.fr:
            i += 1
        self.eventQ.insert(i, [self.t+self.fr,'forces',None])

    def insert(self, event):
        i = 0
        while i < len(self.eventQ) and self.eventQ[i][0] <= event[0]:
            i += 1
        self.eventQ.insert(i, event)

    def getID(self):
        i = 0
        while i in self.IDs:
            i += 1
        self.IDs.add(i)
        return i

    def run(self):
        if len(self.eventQ):
            dt = self.eventQ[0][0]-self.t
            self.t = self.eventQ[0][0]
        
            i = 0
            for i in range(len(self.eventQ)):
                self.eventQ[i][0]-self.t
            self.eventQ = self.process(self.eventQ, dt)

    def collision(self):
        #compute all future collisions
        self.coll, self.ordered = particleTracker.collide(2, self.points, self.mask, self.coll)
        if not len(self.ordered):
            return False
        #don't recompute unless particles change trajectory
        for p in self.points:
            self.mask.add(p)
        #collect next collision, may be multiple
        collilist = []
        for j in range(len(self.ordered)):
            lst = [x for x in self.ordered[j]]
            if self.points[lst[0]]['typ'] != self.points[lst[1]]['typ'] and self.euclidean(self.point[lst[0]['pos'],self.points[lst[1]]['pos'] ) and particleTracker.prune(self.coll[self.ordered[j]]) > 0:
                if len(collilist):
                    #all others collected
                    if particleTracker.prune(self.coll[self.ordered[j]]) == particleTracker.prune(self.coll[collilist[-1]]):
                        collilist.append(self.ordered[j])
                        self.mask -= self.ordered[j]
                else:
                    #first collected
                    collilist.append(self.ordered[j])
                    self.mask -= self.ordered[j]
        #insert collisions into event queue
        if len(collilist):
            for x in collilist:
                self.insert([self.t+particleTracker.prune(self.coll[x]),'collide',x])
            return True
        return False

    def process(self,eventQ,dt):
        i = 0
        while i < len(eventQ) and eventQ[i][0] < 0:
            i += 1
        j = i
        k = eventQ[i][0] 
        while i < len(eventQ) and eventQ[i][0] == k:
            i += 1
        cess = eventQ[j:i]
        eventQ = eventQ[i:]
        print cess
        print eventQ
        #print self.points
        print ''

        for x in cess:
            if x[1] == 'refresh':
                for j in self.points:
                    #erase points
                    if j in self.erase:
                        self.points.pop(j,None)
                        self.IDs.remove(j)
                    else:
                        #update pos and rad of points
                        for i in range(len(self.points[j]['pos'])):
                            self.points[j]['pos'[i] += self.points[j]['vel'][i]*dt
                        self.points[j]['rad'][0] += self.points[j]['rad'][1]*dt
                # create new points
                while len(self.create) != 0:
                    self.points[self.getID()] = self.create.pop()

            if x[1] == 'forces':
                pass
            if x[1] == 'collide':
                self.process([[0,'refresh', None]],dt)
                forc = None
                part = None
                #looks through points involved in collision and extracts force carrier and particle
                for y in x[2]:
                    if self.points[y]['typ'] == 'p':
                        part = self.points[y]
                    elif self.points[y]['typ'] == 'f':
                        forc = self.points[y]
                if forc and part:
                    for i in range(len(part['vel'])):
                        dist = self.euclidean(forc['pos'],part['pos'])
                        if dist != 0:
                            dmv = forc['rad'][1]*(forc['pos'][i]-part['pos'][i])/dist
                            dmv += forc['vel'][i]
                            part['vel'][i] += forc['chr']/forc['rad'][0]
