import particleTracker
import math
import sys
from multiprocessing import Process, Queue
from Queue import Empty,Full
import SocketServer
import time
import json
import copy

class particleSim:
    class sphere:
        def __init__(self, key, point):
            self.key = key
            self.point = point
            self.Set = set()
            self.parents = set()
        def engulf(self, other):
            if self.point == None:
                return True
            if other.point == None:
                return False
            return math.sqrt(sum([ (self.point['pos'][i]-other.point['pos'][i])**2 for i in range(len(self.point['pos'])) ])) <= self.point['rad'][0]-other.point['rad'][0]
        def contain(self, other):
            if self.point == None:
                return True
            return math.sqrt(sum([ (self.point['pos'][i]-other.point['pos'][i])**2 for i in range(len(self.point['pos'])) ])) <= self.point['rad'][0]+other.point['rad'][0]
        def store(self, other):
            if not self.contain(other) or self == other:
                return
            engulfed = False
            for x in self.Set:
                if x.contain(other):
                    x.store(other)
                    if x.engulf(other):
                        engulfed = True
            #not engulfed by child
            if not engulfed:
                self.Set.add(other)
                other.parents.add(self)
            else:
                try:
                    self.Set.remove(other)
                except KeyError:
                    pass
                try:
                    other.parents.remove(self)
                except KeyError:
                    pass

        def collide(self, other):
            pEngulfed = False
            for x in self.parents:
                if x.contain(other):
                    break
            else:
               pEngulfed = True
            #other was up to this point engulfed by self
            if pEngulfed:
                for x in self.parents:
                    oEngulf = False
                    for y in x.Set:
                        if y != self and y.engulf(other):
                            oEngulf = True
                            break
                    #other not engulfed by sibling
                    if not oEngulf:
                        x.Set.add(other)
                    
            elif self.engulf(other):
                for x in self.parents:
                    try:
                        x.Set.remove(other)
                    except KeyError:
                        pass
            #other is already contained, must be exiting
            elif other in self.Set:
                self.Set.remove(other)
            #other is not contained, must be entering
            else:
                self.Set.add(other)
        def Print(self):
            print str(self.key) + ' contains ' + str([str(x.key) for x in self.Set])
            for x in self.Set:
                x.Print()
            
            
            
    def __init__(self):
        #refresh rate
        self.rr = .2

        #force rate
        self.fr = .1

        #rate of force expansion 
        self.c = 1

        self.eventQ = []
        self.create = []
        self.erase = set()
        self.points = dict()
        self.coll = dict()
        self.mask = set()
        self.IDs = set()
        self.space = self.sphere(-1,None)
        self.sDict = dict()


        self.eventQ.append([0,'refresh',None])
        #self.insert([self.t+self.rr,'refresh',None])
        self.insert([self.fr,'forces',None])

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
            #print self.eventQ
            while self.eventQ[0][0] < 0:
                self.eventQ.pop(0)
            dt = self.eventQ[0][0]
        
            for i in range(len(self.eventQ)):
                self.eventQ[i][0] -= dt
            first = True
            i = 0
            eType = self.eventQ[0][1]
            print eType
            self.eventQ = self.process(dt)
            if eType == 'collide':
                self.collision()
            '''
            while i < len(self.eventQ):
                if self.eventQ[i][0] == 0:
                    if first:
                        self.eventQ = self.process(self.eventQ, dt)
                        first = False
                    else:
                        print 'yo'
                        self.eventQ = self.process(self.eventQ, 0)
                else:
                    i += 1
    '''
    def collision(self):
        #compute all future collisions
        before = time.clock()
        self.coll, self.ordered = particleTracker.collide(2, self.points, self.mask, self.coll)
        print time.clock()-before
        #print self.ordered
        #print self.mask
        if not len(self.ordered):
            return False
        #dont recompute unless one of the particles involved changes trajectory
        for p in self.points:
            self.mask.add(p)
        #collect next collision, may be multiple
        collilist = []
        collilist2 = []
        for j in range(len(self.ordered)):
            lst = [x for x in self.ordered[j]]
            if self.points[lst[0]]['typ'] == self.points[lst[1]]['typ'] and not len(collilist):
                collilist2.append(self.ordered[j])
            elif (False or self.points[lst[0]]['typ'] != self.points[lst[1]]['typ']) and self.euclidean(self.points[lst[0]]['pos'],self.points[lst[1]]['pos'] ) and particleTracker.prune(self.coll[self.ordered[j]]) > 0:
                if len(collilist):
                    if particleTracker.prune(self.coll[self.ordered[j]]) == particleTracker.prune(self.coll[collilist[-1]]):
                        collilist.append(self.ordered[j])
                else:
                    collilist.append(self.ordered[j])
        #insert collisions into event queue
        if len(collilist2):
            print collilist2
            for x in collilist2:
                lst = [y for y in x]
                self.sDict[lst[0]].collide(self.sDict[lst[1]])
                self.sDict[lst[1]].collide(self.sDict[lst[0]])
        if len(collilist):
            print collilist
            for x in collilist:
                self.insert([particleTracker.prune(self.coll[x]),'collide',x])
            return True
        return False

    def euclidean(self,pos1,pos2):
        return math.sqrt(sum([ (pos1[i]-pos2[i])**2 for i in range(len(pos1)) ]))
        
    def unitV(self, src, dst):
        return 1 - 2 * (src > dst)
    def process(self,dt):

        i = 0
        while i < len(self.eventQ) and self.eventQ[i][0] < 0:
            i += 1
        j = i
        k = self.eventQ[i][0] 
        while i < len(self.eventQ) and self.eventQ[i][0] == k:
            i += 1
        cess = self.eventQ[j:i]
        self.eventQ = self.eventQ[i:]
        #print cess
        #print eventQ
        #print self.points
        #print ''
    
        if True or x[1] == 'refresh':
            for j in self.points:
                #erase points
                if j in self.erase :
                    self.points.pop(j,None)
                else:
                    #update pos and rad of points
                    for i in range(len(self.points[j]['pos'])):
                        self.points[j]['pos'][i] += self.points[j]['vel'][i]*dt
                    self.points[j]['rad'][0] += self.points[j]['rad'][1]*dt
            #create new points
            while len(self.create) != 0:
                ID = self.getID()
                self.points[ID] = self.create.pop()
                newSp = self.sphere(ID,self.points[ID])
                self.sDict[ID] = newSp
                self.space.store(newSp)
        for x in cess:

            if x[1] == 'forces':
                #self.process([[0,'refresh']],dt)
                for p in [z for z in self.points]:
                    if self.points[p]['typ'] == 'p':
                        newF = dict()
                        newF['pos'] = [y for y in self.points[p]['pos']]
                        #newF['vel'] = [y for y in self.points[p]['vel']]
                        newF['vel'] = [0 for y in self.points[p]['vel']]
                        newF['rad'] = [0, self.c]
                        newF['mss'] = 1
                        newF['typ'] = 'f'
                        newF['chr'] = self.points[p]['chr']
                        ID = self.getID()
                        self.points[ID] = newF
                        newSp = self.sphere(ID, newF)
                        for y in [y for y in self.sDict[p].parents]:
                            y.Set.add(newSp)
                            newSp.parents.add(y)
                            y.Set.remove(self.sDict[p])
                            self.sDict[p].parents.remove(y)
                        newSp.store(self.sDict[p])
                        self.sDict[ID] = newSp
                        
                i = 0 
                while i < len(self.eventQ) and self.eventQ[i][0] <= self.fr:
                    i += 1
                self.eventQ.insert(i, [self.fr,'forces',None])
            if x[1] == 'collide':
                print 'hello', x[2], dt
                #self.process([[0,'refresh', None]],dt)
                forc = None
                part = None
                #looks through points involved in collision and extracts force carrier and particle
                for y in x[2]:
                    if self.points[y]['typ'] == 'p':
                        part = self.points[y]
                        try:
                            self.mask.remove(y)
                        except KeyError:
                            pass
                    elif self.points[y]['typ'] == 'f':
                        forc = self.points[y]
                        #self.mask.remove(y)
                if forc and part:
                    for i in range(len(part['vel'])):
                        dist = self.euclidean(forc['pos'],part['pos'])
                        if dist != 0:
                            dmv = forc['rad'][1]*(part['pos'][i]-forc['pos'][i])/dist
                            dmv += forc['vel'][i]
                            dmv = dmv-math.copysign(1,forc['chr']*part['chr'])*part['vel'][i]
                            #print dmv
                            part['vel'][i] += dmv*forc['chr']/( max(forc['rad'][0],1)**2)*part['chr']*(forc['mss']-part['mss'])
                    spd = self.euclidean(part['vel'], [0 for z in range(len(part))] )
                    if spd >= self.c-1e-5:
                        for i in range(len(part['vel'])):
                            part['vel'][i] *= (self.c-1e-5)/spd
                elif forc and True:
                    lst = [y for y in x[2]]
                    for i in range(len(lst)):
                        self.sDict[lst[0]].collide(self.sDict[lst[1]])
                        self.sDict[lst[1]].collide(self.sDict[lst[0]])
                        
                    #print forc['rad'][0], forc['rad'][1]*dt
        return self.eventQ

class tcpParticleSim(particleSim):

    class MyTCPHandler(SocketServer.BaseRequestHandler):
        def handle(self):
            self.data = self.request.recv(1024).strip()
            #print "{} wrote:".format(self.client_address[0])
            #print self.data
            
            while 1:
                try:
                    x = Q.get(False)
                    print x
                    global dikt
                    dikt[x[0]] = x[1]
                except Empty:
                    break
            if '<points/>' in self.data.lower():
                for key in dikt['points']:
                    temp = dict()
                    for key2 in dikt['points'][key]:
                        temp[key2] = dikt['points'][key][key2]
                    #print temp
                    temp['ID'] = key
                    self.request.sendall("<point>" + json.dumps(temp) + "</point>" )
            
            if '<run/>' in self.data.lower():
                #print 'yeah'
                R.put('<run/>',False)

                #self.request.sendall(self.dikt[ self.data[1:-2].lower() ])

    def f(self,q,r):
        global Q
        global R
        global dikt
        dikt = dict()
        Q = q
        R = r
        HOST, PORT = "localhost", 9998
        server = SocketServer.TCPServer((HOST, PORT), self.MyTCPHandler)
        server.serve_forever()

    def __init__(self):
        particleSim.__init__(self)
        self.q = Queue()
        self.r = Queue()
        self.cess = []
        self.cess.append(Process(target=self.f, args=(self.q,self.r)))
        self.cess[-1].start()
    def run(self):
        particleSim.run(self)
        self.report()
    def report(self):
        pass


test = tcpParticleSim()

temp = dict()
temp['pos'] = [0,1]
temp['vel'] = [-.25,0]
temp['rad'] = [0,0]
temp['chr'] = 1
temp['mss'] = .97
temp['typ'] = 'p'
test.create.append(temp)      


temp = dict()
temp['pos'] = [0,-1]
temp['vel'] = [.25,0]
temp['rad'] = [0,0]
temp['chr'] = -1
temp['mss'] = .97
temp['typ'] = 'p'

test.create.append(temp)      

i = 0
for j in range(23):
    print 'run', i
    i += 1
    test.run()
    #test.q.put( ('points', copy.deepcopy(test.points) ) )
    #print place
    #print ''
    #print test.eventQ
    #print ''
    #print ''
    if j == 1:
        test.collision()

test.space.Print()
while 1:
    x = test.r.get()
    if '<run/>' in x:
        print 'run', i
        i += 1
        test.run()
        test.q.put( ('points', test.points ) )


sys.exit(0)
test.run()
#print test.points
print ''
test.eventQ
print ''
print ''
test.run()
print test.points, test.eventQ

sys.exit(0)
test.eventQ.append([.1,'refresh',None])
test.run()
print test.points, test.eventQ

test.run()
test.run()

print test.points

test.collision()
test.run()
print test.points

test.collision()
test.run()
place = test.points
print place
