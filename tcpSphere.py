from sphere import sphere
from particleAndForce import particle, force, IDer
import multiprocessing
from multiprocessing import Process, Queue
from Queue import Empty,Full
import SocketServer
import json

class tcpSphere(sphere):

    class MyTCPHandler(SocketServer.BaseRequestHandler):
        def handle(self):
            self.data = self.request.recv(1024).strip()
            #print "{} wrote:".format(self.client_address[0])
            #print self.data
            while 1:
                try:
                    x = Q.get(False)
                    #print x
                    dikt[x[0]] = x[1]
                except Empty:
                    break
            if '<points/>' in self.data.lower():
                '''for x in dikt['points']:
                    temp = dict()
                    for key2 in self.dikt['points'][key]:
                        temp[key2] = self.dikt['points'][key][key2]
                    #print temp
                    temp['ID'] = key
                    #self.request.sendall("<point>" + json.dumps(x) + "</point>" )
                    '''
                self.request.sendall("<points>" + json.dumps(dikt['points']) + "</points>")
            if '<run/>' in self.data.lower():
                print 'yeah'
                R.put('<run/>',False)

                #self.request.sendall(self.dikt[ self.data[1:-2].lower() ])
            self.request.close()

    def f(self,q,r):
        global Q
        global R
        global dikt
        dikt = dict()
        Q = q
        R = r
        HOST, PORT = "localhost", 9999
        server = SocketServer.TCPServer((HOST, PORT), self.MyTCPHandler)
        server.serve_forever()

    def __init__(self, key, pos, rad, vel):
        sphere.__init__(self, key, pos, rad, vel)
        m = multiprocessing.Manager()
        self.q = m.Queue()
        self.r = m.Queue()
        self.cess = []
        self.cess.append(Process(target=self.f, args=(self.q,self.r)))
        self.cess[-1].start()
    def run(self):
        particleSim.run(self)
        self.report()
    def report(self):
        pass

if __name__=="__main__":
    space = tcpSphere(-1,[0,0], None,[0,0])
    ider = IDer()
    bonds = dict()
    part = particle(ider.getID(), [300,200], [0,0], [0,.0], 3, .00, .0001, 10,ider, bonds)
    space.contain[part.key] = part
    part.parents[space.key] = space
    part2 = particle(ider.getID(), [250,200], [0,0], [0,.0], 3, .00, .0001, 10,ider, bonds)
    space.contain[part2.key] = part2
    part2.parents[space.key] = space
    bonds[frozenset([part.key,part2.key])] = {'k':0.000000001, 'type':0, 'eqlen':40}


    i = 0
    while 1:
        x = space.r.get()
        if '<run/>' in x:
            print 'run', i
            i += 1
            space.internalCollision()
            nextEvent = space.nextEvent()
            advance = nextEvent[0]
            space.progress(advance)
            space.execute()
            #print part.vel
            print ''
            for x in space.allSpheres():
                if x != space and x.contains(part) and x.contains(part2) and isinstance(x,force):
                    print 'deleting', x.key
                    x.delete()
            temp = [y.toDict() for y in space.allSpheres() - set([space]) ]
            
            #print temp
            #print nextEvent
            #print part.parents, sum([isinstance(x,force) for x in part.parents])
            space.q.put( ('points', temp) )
