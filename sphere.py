#from multiprocessing import Process, Queue, Manager, Lock
from operator import itemgetter, attrgetter
from Queue import Empty,Full
import math
import sys

#M = Manager() #in order to make multiprocess, one needs to make the instance variables manager types

def unwrap_self_f(arg, **kwarg):
    return C.f(*arg, **kwarg)
class sphere:
    def __init__(self, key, pos, rad, vel):
        self.key = key
        self.pos = pos
        self.rad = rad
        #if self.rad != None:
        #    self.rad = M.list(self.rad)
        self.vel = vel
        self.contain = dict()
        self.touch = dict()
        self.parents = dict()
        self.velChange = True
        self.eventQ = []
        self.oldTot = []

    def quadratic(self, a, b, c):
        #print a,b,c
        if a == 0 and b != 0:
            return tuple([-1*c / (1.0*b)])
        elif b == 0 and a != 0:
            try:
                return -1*math.sqrt(-1*c/a),math.sqrt(-1*c/a)
            except ValueError:
                return None, None
        try:
            disc = math.sqrt(b**2 - 4*a*c)
        except ValueError:
            return None, None
        try:
            val1 = (-1*b - disc) / (2.0*a)
        except ZeroDivisionError:
            val1 = None
        try:
            val2 = (-1*b + disc) / (2.0*a)
        except ZeroDivisionError:
            val2 = None
        return val1, val2

    @staticmethod
    def euclidean(vec1,vec2):
        dist = 0.0
        for i in range(max(len(vec1),len(vec2))):
            try:
                x1 = vec1[i]
            except IndexError:
                x1 = 0
            try:
                x2 = vec2[i]
            except IndexError:
                x2 = 0
            dist += (x1-x2)**2
        dist **= 0.5
        return dist

    @staticmethod
    def eventEquals(event1, event2):
        if event1[0] != event2[0]:
            return False
        if event1[1] != event2[1]:
            return False
        if type(event1[2]) != type(event2[2]):
            return False
        if len(event1[2]) != len(event2[2]):
            return False
        if type(event1[2]) == type([]):
            for i in range(len(event1[2])):
                if event1[2][i] != event2[2][i]:
                    return False
        if (type(event1[2]) == type(set()) or type(event1[2]) == type(frozenset())) and len(event1[2] ^ event2[2]) != 0:
            return False
        #print event1, event2, [x for x in event1[2]],[x for x in event2[2]]
        return True
    
    @staticmethod
    def containsEqualEvent(event, collection):
        #print event, [x.key for x in event[2]]
        for x in collection:
            if sphere.eventEquals(event,x):
                return True
        return False

    def eventMove(self, oldP, newP=None): #also deletes
        events = []
        for x in oldP:
            i = 0
            while i < len(x.eventQ):
                if self.key in x.eventQ[i][2]:
                    temp = x.eventQ.pop(i)
                    if temp not in events:
                        events.append(temp)
                else:
                    i += 1
        if newP != None:
            for x in newP:
                for y in events:
                    x.insert(y)
    
    def insert(self,event):
        i = 0
        #self.lock.acquire()
        while i < len(self.eventQ) and self.eventQ[i][0] <= event[0]:
            if sphere.eventEquals(self.eventQ[i],event):
                return
            i += 1
        self.eventQ.insert(i, event)
        #self.lock.release()
    
    def inject(self, other):
        if self.geometricOverlap(other):
            containedByChild = False
            for x in self.contain:
                self.contain[x].inject(other)
                if self.contain[x].geometricContains(other):
                    containedByChild = True
                if other.geometricContains(self.contain[x]):
                    del self.contain[x].parents[self.key]
                    self.contain[x].parents[other.key] = other
                    other.contain[x] = self.contain[x]
                    del self.contain[x]
            if not containedByChild and self.geometricContains(other):
                self.contain[other.key] = other
                other.parents[self.key] = self
        

    def geometricContains(self,other):
        if self.rad == None:
            return True
        if self.euclidean(self.pos,other.pos) <= self.rad[0]-other.rad[0] and self.rad[0] != 0:
            return True
        else:
            return False
        
    def geometricOverlap(self,other):
        if self.rad == None:
            return True
        if self.euclidean(self.pos,other.pos) <= self.rad[0]+other.rad[0]:
            return True
        else:
            return False


    def action(self):
        return []

    def toDict(self):
        temp = dict()
        temp['pos'] = self.pos
        temp['rad'] = self.rad
        temp['vel'] = self.vel
        temp['ID'] = self.key
        return temp

    def delete(self):
        for x in self.parents.values():
            del x.contain[self.key]
            self.eventMove(set([x]))
            for key in self.contain:
                if not x.contains(self.contain[key]):
                    x.contain[key] = self.contain[key]
                    self.contain[key].parents[x.key] = x
        for x in self.touch.values():
            del x.touch[self.key]
        for x in self.contain.values():
            #print self.key, x.key
            del x.parents[self.key]

    def contains(self, other):
        if self == other:
            return False
        if other.key in self.contain:
            return True
        for key in self.contain:
            if self.contain[key].contains(other):
                return True
        return False

    def traverse(self):
        print self.key, '{'
        for key in self.contain:
            self.contain[key].traverse()
        print '}'

    def overlap(self,other):
        if not self.rad or not other.rad or not self.rad[0] or not other.rad[0]:
            return
        if other.key in self.touch:
            del self.touch[other.key]
            other.eventMove(set([self]))
        else:
            self.touch[other.key] = other

    @staticmethod
    def allSpheresWrapper(obj, q=None):
        obj.allSpheres(q)
    
    def allSpheres(self, q=None):
        #r = Queue()
        #cess = []
        #for x in self.contain.values():
        #    cess.append(Process(target=sphere.allSpheresWrapper, args=(x,r)))
        #    cess[-1].start() 
        i = 0
        output = [self]
        for x in self.contain.values():
            output.extend(x.allSpheres())
        #while i < len(cess):
        #    output += r.get()
        #    i += 1
        if q:
            q.put(output)
        else:
            return set(output)
        

    
    def engulf(self,other):
        if self.rad[0] == other.rad[0]:     #when two spheres are perfectly conincident and one had just contained the other
            if self.key in other.contain:
                del other.contain[self.key]  #remove from sphere it is leaving
                del self.parents[other.key]  #remove parent relationship
                for key in [x for x in other.parents]:
                    other.parents[key].contain[self.key] = self     #add to parents of parent it is leaving
                    del other.parents[key].contain[other.key]
                    self.parents[key] = other.parents[key]     #add new parent relationships
                for key in [x for x in other.parents]:
                    del other.parents[key]
                other.parents[self.key] = self
                self.contain[other.key] = other
                #self.eventMove(set([other]),[self.parents.values()[0]]) #events need to follow one of the spheres it involves
                self.eventMove(set([other]))
                #other.eventMove(self.parents.values(),set([self]))
                other.eventMove(self.parents.values())
                other.engulfedBy(self)
            elif other.key in self.contain:
                other.engulf(self)
        if self.rad[0] <= other.rad[0]:
            return
        if other.key in self.contain:
            #print 'yo'
            del self.contain[other.key]
            del other.parents[self.key]
            if self.rad[0] and other.rad[0]:
                self.touch[other.key] = other
            for key in self.parents:
                for x in self.parents[key].contain:
                    if self.parents[key].contain[x].contains(other):
                        break
                else:
                    self.parents[key].contain[other.key] = other
                    other.parents[key] = self.parents[key]
                    #other.eventMove(set([self]), set([self.parents[key]]) )
                    other.eventMove(set([self]) )
            other.eventMove(set([self]))
            other.engulfedBy(self)
        else:
            self.contain[other.key] = other
            if self.rad[0] and other.rad[0]:
                del self.touch[other.key]
                del other.touch[self.key]
            other.eventMove(other.parents.values(),set([self]))
            for key in [y for y in other.parents]:
                if key in self.parents:
                    del self.parents[key].contain[other.key]
                    del other.parents[key]
            other.parents[self.key] = self
            other.engulfedBy(self)

    def engulfedBy(self, other):
        pass
         
        
    def execute(self, done=None):
        if done == None:
            done = []
        i = 0
        #print self.key
        while i < len(self.eventQ) and self.eventQ[i][0] <= 0:
            #print self.eventQ[i]
            if self.eventQ[i][0] < 0 or sphere.containsEqualEvent(self.eventQ[i],done):
                self.eventQ.pop(i)
                
            elif self.eventQ[i][0] == 0:
                #print self.key, self.eventQ[i]
                #print self.contain, self.touch
                temp = [x for x in self.eventQ[i][2]]
                error = False
                for j in range(len(temp)):
                    if temp[j] == self.key:
                        temp[j] = self
                    if temp[j] in self.contain:
                        temp[j] = self.contain[temp[j]]
                    elif temp[j] in self.touch:
                        temp[j] = self.touch[temp[j]]
                    if type(temp[j]) == type(1):
                        print 'error: ' + str(temp[j]) + ' not in ' + str(self.key)
                        error = True
                if error:
                    i += 1
                    continue
                #print temp, self.pos
                #print self.contain, self.touch
                #print done
                if self.eventQ[i][1] == 'touch':
                    print self.key, 'touch', [x for x in self.eventQ[i][2]]
                    done.append([x for x in self.eventQ[i]])
                    self.eventQ.pop(i)
                    temp[0].overlap(temp[1])
                    temp[1].overlap(temp[0])
                elif self.eventQ[i][1] == 'contain':
                    print self.key, 'contain', [x for x in self.eventQ[i][2]], id(self.eventQ[i])
                    tlen = len(self.eventQ) #event can be moved during engulf call
                    temp[0].engulf(temp[1])
                    from particleAndForce import particle, force
                    if type(temp[0]) is force and type(temp[1]) is particle:
                        print '*****************************'
                        temp[1].forced(temp[0])
                    if tlen == len(self.eventQ):
                    	done.append(self.eventQ.pop(i))
                elif self.eventQ[i][1] == 'emit':
                    print self.key, 'emit', self.eventQ[i][2][0]
                    temp[0].emit = True
                    done.append(self.eventQ.pop(i))
                    temp[0].emission()
            else:
                break
        for key in [x for x in self.contain]:
            if key in self.contain:
                self.contain[key].execute(done)
            
    @staticmethod
    def progressWrapper(obj, dt, done=None):
        obj.progress(dt, done)

    def progress(self, dt, done=None):
        #print self.key, done
        if done == None:
            #done = M.dict()
            done = dict()
        done[self.key] = None
        for i in range(len(self.pos)):
            self.pos[i] += self.vel[i]*dt
        if self.rad != None:
            #print '******************'
            #temp = [x for x in self.rad]
            #print self.rad[0] + self.rad[1]*dt
            self.rad[0] += self.rad[1]*dt
            self.rad = self.rad
        for i in range(len(self.eventQ)):
            temp = self.eventQ[i]
            temp[0] -= dt
            if temp[0] < 1.0*10**-10 and temp[0] > 0:
                temp[0] = 0
            self.eventQ[i] = temp
        cess = []
        for x in self.contain:
            if x not in done:
                self.contain[x].progress(dt, done)
                #done[self.key] = None
                #cess.append(Process(target=sphere.progressWrapper, args=(self.contain[x], dt, done)))
                #cess[-1].start()
        for p in cess:
            p.join()
            
    @staticmethod
    def nextEventWrapper(obj, q=None):
        obj.nextEvent(q)
    
    def nextEvent(self, q=None):
        #r = Queue()
        #cess = []
        #for x in self.contain.values():
            #cess.append(Process(target=sphere.nextEventWrapper, args=(x,r)))
            #cess[-1].start() 
        output = None
        for x in self.eventQ:
            if x[0] > 0:
                output = x
                break
        i = 0
        #while i < len(cess):
        for x in self.contain.values():
            #temp = r.get()
            temp = x.nextEvent()
            if output == None or (temp != None and temp[0] < output[0] and temp[0] > 0):
                output = temp
            i += 1
        if q:
            q.put(output)
        else:
            return output

    @staticmethod
    def internalCollisionWrapper(obj, done=None):
        obj.internalCollision(done)

    def internalCollision(self, done=None):
        for x in self.action():
            self.insert(x)
        if not len(self.contain) and not len(self.touch):
            return
        if done == None:
            done = dict()
            done[self.key] = None
        total = set(self.contain.values()) | set(self.touch.values())
        total = [x for x in total]
        #if self.key == 1:
        #    print 'total', total, '~~~~~~~~~~~~~~~~~~~~~~~~~'
        intVelChange = False
        for x in total:
            if x.velChange:
                intVelChange = True
        cess = []
        for x in self.contain.values():
            if x.key not in done:
                done[x.key] = None
                x.internalCollision(done)
                #cess.append(Process(target=sphere.internalCollisionWrapper, args=(x,done)))
                #cess[-1].start()
        #if self.key == 1:
        #    print total, self.oldTot
        if len(set([x.key for x in total])-set(self.oldTot)) or intVelChange or self.velChange:
            
            if self.rad != None: #Meaning, it isn't the space
                total.append(self)
            i = 0
            while i < len(self.eventQ): #if velocity changes, collisions need to be recomputed
                for x in self.eventQ[i][2]:
                    if x in self.contain and self.contain[x].velChange and len(self.eventQ[i][2]) > 1:
                        self.eventQ.pop(i)
                        break
                    else:
                        i += 1
            
            for i in range(len(total)):
                for j in range(i+1,len(total)):
                    #print self.key, total[i].collide(total[j]), 'word'
                    #if not total[i].velChange and not total[j].velChange:
                    #    if not total[i].key in set([x.key for x in total]) - set(self.oldTot):
                    #        if not total[j].key in set([x for x in total]) - set(self.oldTot):
                    #            if self.key ==2 or self.key == 3:
                    #                print total[i].key, total[j].key, [x.key for x in total], self.oldTot
                    #            continue
                    for x in total[i].collide(total[j]):
                        if (total[i].rad[0] == 0 or total[j].rad[0] == 0) and x[1] == 'touch':
                            pass
                        else:
                            x[0] = round(x[0]*10**5)/10.0**5
                            #if 1 in x[2] or 0 in x[2]:
                            #    print 'hey', self.key, x
                            self.insert(x)
                            #if 1 in x[2] or 0 in x[2]:
                            #    print 'hey', self.key, self.eventQ
        for p in cess:
            p.join()
        for x in total:
            x.velChange = False
        #if self.key == 2 or self.key == 3:
        #    print self.key, self.eventQ, [x.key for x in total], self.oldTot
        #self.oldTot = M.list([x.key for x in set(total) - set([self])])
        self.oldTot = list([x.key for x in set(total) - set([self])])

    def collide(self, other):
        a = 0
        b = 0
        c = 0
        for k in range(len(self.pos)):
            a += (self.vel[k] - other.vel[k])**2
            b += 2*(self.vel[k] - other.vel[k])*(self.pos[k] - other.pos[k])
            c += (self.pos[k] - other.pos[k])**2
        
        a2 = a
        b2 = b
        c2 = c

        a -= (self.rad[1] + other.rad[1])**2
        b -= 2*(self.rad[1] + other.rad[1])*(self.rad[0] + other.rad[0])
        c -= (self.rad[0] + other.rad[0])**2

        a2 -= (self.rad[1] - other.rad[1])**2
        b2 -= 2*abs(self.rad[1] - other.rad[1])*abs(self.rad[0] - other.rad[0])
        c2 -= (self.rad[0] - other.rad[0])**2
        output = []
        quad = self.quadratic(a,b,c)
        for x in set(quad):
            if x >= 0 and x != None:
                output.append([x,'touch',frozenset([self.key,other.key])])
        quad = self.quadratic(a2,b2,c2)
        for x in set(quad):
            if x >= 0 and x != None:
                if self.rad[1]*x + self.rad[0] >= other.rad[1]*x + other.rad[0]:
                    output.append([x,'contain',[self.key,other.key]])
                else:
                    output.append([x,'contain',[other.key,self.key]])
        return output

if __name__=="__main__":
    space = sphere(-1, [0,0], None, [0,0])
    
    sph1 = sphere(0, [0,2], [1,0], [0,-1])
    #space.contain[sph1.key] = sph1
    #sph1.parents[space.key] = space
    space.inject(sph1)    

    sph2 = sphere(1,[0,-2], [1,0], [0,1])
    space.contain[sph2.key] = sph2
    sph2.parents[space.key] = space
    
    sph3 = sphere(2,[0,-2],[0,0],[0,1])
    sph2.contain[sph3.key] = sph3
    sph3.parents[sph2.key] = sph2
    
    sph4 = sphere(3,[-2,0], [1,0], [1,0])
    space.contain[sph4.key] = sph4
    sph4.parents[space.key] = space
    
    for i in range(5):
        space.internalCollision()
        #print 'space','Event', space.eventQ
        #print 'sph0','Event', sph1.eventQ
        #print 'sph1','Event', sph2.eventQ
        #print 'sph3','Event', sph4.eventQ
        #print 'space', space.touch
        #print 'sph2', sph2.touch
        event= space.nextEvent()
        print event, '~~~~~~~~~~'
        space.progress(event[0])
        space.execute()
        space.traverse()
        print ' '

    print sph1.pos, sph2.pos, sph3.pos, sph4.pos

