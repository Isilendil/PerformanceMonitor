#-*-coding:utf-8-*-
from __future__ import division
import time
import wx
from matplotlib.figure import Figure
import matplotlib.font_manager as font_manager
import numpy as np
from matplotlib.backends.backend_wxagg import \
  FigureCanvasWxAgg as FigureCanvas
# wxWidgets object ID for the timer
TIMER_ID = wx.NewId()
# number of data points
POINTS = 300
A = None

def cpuinfo():
  fp = open("/proc/stat",'r')
  data = fp.readline()
  data = data[5:]
  data = data.split()
  for i in range(len(data)):
    data[i] = int(data[i])
  fp.close()
  return data

def calusage(inp):
  data = inp
  user = data[0]
  nice = data[1]
  sys = data[2]
  idle = data[3]
  iowait = data[4]
  irq = data[5]
  softirq = data[6]
  all1 = user + nice + sys +idle + iowait + irq + softirq
  idle1 = idle
  data = cpuinfo()
  user = data[0]
  nice = data[1]
  sys = data[2]
  idle = data[3]
  iowait = data[4]
  irq = data[5]
  softirq = data[6]
  all2 = user + nice +sys +idle + iowait + irq +softirq
  idle2 =idle
  usage = 100*(all2-all1-(idle2-idle1))/(all2-all1)
  return [data,usage]

class PlotFigure(wx.Frame):
    """Matplotlib wxFrame with animation effect"""
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, title="CPU Usage Monitor", size=(600, 400))
        # Matplotlib Figure
        self.fig = Figure((6, 4), 100)
        # bind the Figure to the backend specific canvas
        self.canvas = FigureCanvas(self, wx.ID_ANY, self.fig)
        # add a subplot
        self.ax = self.fig.add_subplot(111)
        # limit the X and Y axes dimensions
        self.ax.set_ylim([0, 100])
        self.ax.set_xlim([0, POINTS])
       
        self.ax.set_autoscale_on(False)
        self.ax.set_xticks([])
        # we want a tick every 10 point on Y (101 is to have 10
        self.ax.set_yticks(range(0, 101, 10))
        # disable autoscale, since we don't want the Axes to ad
        # draw a grid (it will be only for Y)
        self.ax.grid(True)
        # generates first "empty" plots
        self.user = [None] * POINTS
        self.l_user,=self.ax.plot(range(POINTS),self.user,label='User %')

        # add the legend
        self.ax.legend(loc='upper center',
                           ncol=4,
                           prop=font_manager.FontProperties(size=10))
        # force a draw on the canvas()
        # trick to show the grid and the legend
        self.canvas.draw()
        # save the clean background - everything but the line
        # is drawn and saved in the pixel buffer background
        self.bg = self.canvas.copy_from_bbox(self.ax.bbox)
        # bind events coming from timer with id = TIMER_ID
        # to the onTimer callback function
        wx.EVT_TIMER(self, TIMER_ID, self.onTimer)

    def onTimer(self, evt):
        """callback function for timer events"""
        # restore the clean background, saved at the beginning
        self.canvas.restore_region(self.bg)
                # update the data
        global A
        if(A==None):
          A = cpuinfo()
          temp = 0
        else:
          data = calusage(A)
          A = data[0]
          print A
          temp = data[1]
        # temp =np.random.randint(10,80)
        self.user = self.user[1:] + [temp]
        # update the plot
        self.l_user.set_ydata(self.user)
        # just draw the "animated" objects
        self.ax.draw_artist(self.l_user)# It is used to efficiently update Axes data (axis ticks, labels, etc are not updated)
        self.canvas.blit(self.ax.bbox)
if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = PlotFigure()
    t = wx.Timer(frame, TIMER_ID)
    t.Start(50)
    frame.Show()
    app.MainLoop()
    
