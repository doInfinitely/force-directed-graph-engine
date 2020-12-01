import wx
from fdg import fdg

class MainWindow(wx.Frame):
    def __init__(self,parent, title):
        super(MainWindow, self).__init__(parent, title=title, size=(1500, 1000))
        self.CreateStatusBar() # A Status bar in the bottom of the window
        #self.panel.Bind(wx.EVT_LEFT_DOWN, self.onLeftDown)
        #self.panel.Bind(wx.EVT_LEFT_DCLICK, self.onLeftDClick)
        #self.panel.Bind(wx.EVT_RIGHT_DOWN, self.onRightDown)
        self.Bind(wx.EVT_PAINT, self.onPaint)
        #self.Bind(wx.calendar.EVT_CALENDAR_SEL_CHANGED, self.OnCalendarChange)
        #self.Bind(wx.EVT_BUTTON, self.OnCommit, self.commit)
        #self.Bind(wx.EVT_BUTTON, self.OnRevert, self.revert)

        self.graph = fdg()
        charge1 = fdg.pCharge(dim=5)
        charge1.movP((200,150,128,128,128))
        charge2 = charge1.spawnCharge(500)
        charge3 = charge1.spawnCharge(500)
        charge4 = charge1.spawnCharge(500)
        #charge4 = fdg.pCharge(dim=2,mass=1000.0, charge=-1000.0)
        #charge2.movP((200,200))
        #charge3.movP((200,150))
        #charge4.movP((175,175))
        self.graph.charges.add(charge1)
        self.graph.charges.add(charge2)
        self.graph.charges.add(charge3)
        self.graph.charges.add(charge4)
        self.graph.edges.add((charge1,charge2))
        self.graph.edges.add((charge1,charge3))
        self.graph.edges.add((charge2,charge3))
        self.graph.edges.add((charge4,charge2))
        #self.graph.edges.add((charge4,charge1))
    	self.Show(True)
        self.charge = charge1
        self.run(100)

    def onPaint(self,e):
        topcorner = [0,0]
        drawspace =  list(self.GetSize())

        dc = wx.PaintDC(self)
        dc.SetMapMode(wx.MM_METRIC)
        dc.SetPen(wx.Pen('#d4d4d4'))
        dc.SetBrush(wx.Brush('#000000'))
        for p in self.graph.charges:
            print p.pos
            dc.SetBrush(wx.Brush("#" + "%02x" % max(0,min(255, round(p.pos[2])+127 )) + "%02x" % max(0,min(255, round(p.pos[3])+127 )) + "%02x" % max(0,min(255, round(p.pos[4])+127 )) ))
            dc.DrawCircle(p.pos[0],p.pos[1],5)

    def run(self,time):
        wx.FutureCall(time, self.run, time)
        for i in range(100):
            self.graph.run(time/10000.0)
        #print self.charge.pos
        #print self.charge.acc
        self.Refresh()


app = wx.App(False)
frame = MainWindow(None, 'Force Directed Graph Viewer')
app.MainLoop()
