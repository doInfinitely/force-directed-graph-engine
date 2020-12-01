from multiprocessing import Process, Queue, Lock, Manager, Value


class C:
    @staticmethod
    def incMwrapper(obj, num):
        return obj.inc(num)

    def __init__(self):
        self.i = Value('i', 0)
        
    def inc(self, num=1):
        for i in range(num):
            self.i.value += 1
        print self.i.value
    def incM(self, num=1):
        cess = []
        for i in range(num):
            cess.append(Process(target=C.incMwrapper,args=(self,1)))
            cess[-1].start()
        for p in cess:
            p.join()
        print self.i.value

test = C()

test.incM(100)
        
