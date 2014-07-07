#!/usr/bin/env python

import wx
import time
import sys
import os
import threading
import math

import numpy as np
import matplotlib


matplotlib.use("WXAgg")

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as NavigationToolbar
from matplotlib.ticker import MultipleLocator, FuncFormatter

import pylab
from matplotlib import pyplot

LENGTH = 200
TIMERLENGTH = 50

ProcessorFileName = '/proc/stat'
MemoryFileName = '/proc/meminfo'
DiskFileName = '/proc/vmstat'
NetworkFileName = '/proc/net/dev'
ProcessorRecordFileName = 'Processor.data'
MemoryRecordFileName = 'Memory.data'
DiskRecordFileName = 'Disk.data'
NetworkRecordFileName = 'Network.data'
NullFileName = '/dev/null'

class PageMonitoring(wx.Panel):
  def __init__(self, parent, parameter1, parameter2, parameter3):
    wx.Panel.__init__(self, parent)

    self.Figure = matplotlib.figure.Figure((parameter1, parameter2), parameter3)
    self.FigureCanvas = FigureCanvas(self, -1, self.Figure)
    self.axes = self.Figure.add_subplot(1,1,1)

    self.NavigationToolbar = NavigationToolbar(self.FigureCanvas)

    self.SubBoxSizer = wx.BoxSizer(wx.HORIZONTAL)
    self.SubBoxSizer.Add(self.NavigationToolbar, proportion = -1, border = 2, flag = wx.ALL | wx.EXPAND)

    self.TopBoxSizer = wx.BoxSizer(wx.VERTICAL)
    self.TopBoxSizer.Add(self.SubBoxSizer, proportion = -1, border = 2, flag = wx.ALL | wx.EXPAND)
    self.TopBoxSizer.Add(self.FigureCanvas, proportion = -10, border = 2, flag = wx.ALL | wx.EXPAND)

    self.SetSizer(self.TopBoxSizer)

    self.axes.grid(True)


  def UpdatePlot(self):
    self.FigureCanvas.draw()


class PageMonitoring2(wx.Panel):
  def __init__(self, parent, parameter1, parameter2, parameter3):
    wx.Panel.__init__(self, parent)

    self.panel1 = PageMonitoring(self, parameter1, parameter2, parameter3)
    self.panel2 = PageMonitoring(self, parameter1, parameter2, parameter3)
    self.TopBoxSizer = wx.BoxSizer(wx.HORIZONTAL)
    self.TopBoxSizer.Add(self.panel1, proportion = -1, border = 2, flag = wx.ALL | wx.EXPAND)
    self.TopBoxSizer.Add(self.panel2, proportion = -1, border = 2, flag = wx.ALL | wx.EXPAND)
    self.SetSizer(self.TopBoxSizer)
    '''
    self.Figure1 = matplotlib.figure.Figure((6,4.5), 70)
    self.FigureCanvas1 = FigureCanvas(self, -1, self.Figure1)
    self.Figure2 = matplotlib.figure.Figure((6,4.5), 70)
    self.FigureCanvas2 = FigureCanvas(self, -1, self.Figure2)
    self.axes1 = self.Figure1.add_subplot(1,1,1)
    self.axes2 = self.Figure2.add_subplot(1,1,1)

    self.NavigationToolbar1 = NavigationToolbar(self.FigureCanvas1)
    self.NavigationToolbar2 = NavigationToolbar(self.FigureCanvas2)

    self.SubBoxSizer1 = wx.BoxSizer(wx.VERTICAL)
    self.SubBoxSizer1.Add(self.NavigationToolbar1, proportion = -1, border = 2, flag = wx.ALL | wx.EXPAND)
    self.SubBoxSizer1.Add(self.FigureCanvas1, proportion = -10, border = 2, flag = wx.ALL | wx.EXPAND)

    self.SubBoxSizer2 = wx.BoxSizer(wx.VERTICAL)
    self.SubBoxSizer2.Add(self.NavigationToolbar2, proportion = -1, border = 2, flag = wx.ALL | wx.EXPAND)
    self.SubBoxSizer2.Add(self.FigureCanvas2, proportion = -10, border = 2, flag = wx.ALL | wx.EXPAND)

    self.TopBoxSizer = wx.BoxSizer(wx.HORIZONTAL)
    self.TopBoxSizer.Add(self.SubBoxSizer1, proportion = -1, border = 2, flag = wx.ALL | wx.EXPAND)
    self.TopBoxSizer.Add(self.SubBoxSizer2, proportion = -1, border = 2, flag = wx.ALL | wx.EXPAND)

    self.SetSizer(self.TopBoxSizer)

    #self.axes.set_ylim([0, 100])
    #self.axes.set_xlim([0, LENGTH])
    #self.axes.set_yticks(range(0, 101, 10))
    #self.axes.set_xticks([])
    self.axes1.grid(True)
    self.axes2.grid(True)
    #self.axes.set_autoscale_on(False)

  def UpdatePlot1(self):
    self.FigureCanvas1.draw()

  def UpdatePlot2(self):
    self.FigureCanvas2.draw()
'''





class PageGeneral(wx.Panel):
  def __init__(self, parent):
    wx.Panel.__init__(self, parent)
    #wx.StaticText(self, label = 'Processor')


class MyFrame(wx.Frame):
  def __init__(self, parent, id):
    wx.Frame.__init__(self, parent, id, 'Performance Monitor', size = (800, 600), style = wx.DEFAULT_FRAME_STYLE)
    #wx.Frame.__init__(self, parent, id, 'Performance Monitor', size = (800, 600), style = wx.DEFAULT_FRAME_STYLE^wx.RESIZE_BORDER)
    self.openAlready = False

    self.processorRecordFile = open(NullFileName, 'w')
    self.memoryRecordFile = open(NullFileName, 'w')
    self.diskRecordFile = open(NullFileName, 'w')
    self.networkRecordFile = open(NullFileName, 'w')

    
    self.length = LENGTH

    statusBar = self.CreateStatusBar()

    self.MyCreateMenuBar()
    self.MyCreateToolBar()

    self.notebook = wx.Notebook(self)

    self.pageGeneral = PageGeneral(self.notebook)
    self.notebook.AddPage(self.pageGeneral, 'General')

    self.pageProcessor = PageMonitoring(self.notebook, 8, 4.5, 100)
    self.notebook.AddPage(self.pageProcessor, 'Processor')

    self.pageMemory = PageMonitoring(self.notebook, 8, 4.5, 100)
    self.notebook.AddPage(self.pageMemory, 'Memory')

    self.pageDisk = PageMonitoring2(self.notebook, 6, 6, 70)
    self.notebook.AddPage(self.pageDisk, 'Disk')

    self.pageNetwork = PageMonitoring2(self.notebook, 6, 6, 70)
    self.notebook.AddPage(self.pageNetwork, 'Network')

    self.processorUtilization = [None] * self.length 
    self.memoryUtilization = [None] * self.length 
    self.diskRead = [None] * self.length 
    self.diskWrite = [None] * self.length 
    self.networkReceive = [None] * self.length 
    self.networkTransmit = [None] * self.length 


    self.MyCreateTimer()

    self.dataProcessor, = self.pageProcessor.axes.plot(range(1, self.length+1), self.processorUtilization, label = '%')
    self.pageProcessor.UpdatePlot()
    self.pageProcessor.bg = self.pageProcessor.FigureCanvas.copy_from_bbox(self.pageProcessor.axes.bbox)

    self.pageProcessor.axes.set_ylim([0, 100])
    self.pageProcessor.axes.set_xlim([0, LENGTH])
    self.pageProcessor.axes.set_yticks(range(0, 101, 10))
    self.pageProcessor.axes.set_xticks([])
    self.pageProcessor.axes.set_autoscale_on(False)

    self.dataMemory, = self.pageMemory.axes.plot(range(1, self.length+1), self.memoryUtilization, label = '%')
    self.pageMemory.UpdatePlot()
    self.pageMemory.bg = self.pageMemory.FigureCanvas.copy_from_bbox(self.pageMemory.axes.bbox)

    self.pageMemory.axes.set_ylim([0, 100])
    self.pageMemory.axes.set_xlim([0, LENGTH])
    self.pageMemory.axes.set_yticks(range(0, 101, 10))
    self.pageMemory.axes.set_xticks([])
    self.pageMemory.axes.set_autoscale_on(False)

    self.dataDiskRead, = self.pageDisk.panel1.axes.plot(range(1, self.length+1), self.diskRead, label = '%')
    self.pageDisk.panel1.UpdatePlot()
    self.pageDisk.panel1.bg = self.pageDisk.panel1.FigureCanvas.copy_from_bbox(self.pageDisk.panel1.axes.bbox)
    self.dataDiskWrite, = self.pageDisk.panel2.axes.plot(range(1, self.length+1), self.diskWrite, label = '%')
    self.pageDisk.panel2.UpdatePlot()
    self.pageDisk.panel2.bg = self.pageDisk.panel2.FigureCanvas.copy_from_bbox(self.pageDisk.panel2.axes.bbox)

    self.pageDisk.panel1.axes.set_xlim([0, LENGTH])
    self.pageDisk.panel1.axes.set_ylim([0, 1024])
    self.pageDisk.panel1.axes.set_yticks(range(0, 1024, 100))
    self.pageDisk.panel1.axes.set_autoscale_on(False)
    self.pageDisk.panel2.axes.set_xlim([0, LENGTH])
    self.pageDisk.panel2.axes.set_ylim([0, 1024])
    self.pageDisk.panel2.axes.set_yticks(range(0, 1024, 100))
    self.pageDisk.panel2.axes.set_autoscale_on(False)


    self.dataNetworkReceive, = self.pageNetwork.panel1.axes.plot(range(1, self.length+1), self.networkReceive)
    self.pageNetwork.panel1.UpdatePlot()
    self.pageNetwork.panel1.bg = self.pageNetwork.panel1.FigureCanvas.copy_from_bbox(self.pageNetwork.panel1.axes.bbox)
    self.dataNetworkTransmit, = self.pageNetwork.panel2.axes.plot(range(1, self.length+1), self.networkTransmit)
    self.pageNetwork.panel2.UpdatePlot()
    self.pageNetwork.panel2.bg = self.pageNetwork.panel2.FigureCanvas.copy_from_bbox(self.pageNetwork.panel2.axes.bbox)

    self.pageNetwork.panel1.axes.set_xlim([0, LENGTH])
    self.pageNetwork.panel1.axes.set_ylim([0, 100])
    self.pageNetwork.panel1.axes.set_yticks(range(0, 101, 10))
    self.pageNetwork.panel1.axes.set_autoscale_on(True)
    self.pageNetwork.panel2.axes.set_xlim([0, LENGTH])
    self.pageNetwork.panel2.axes.set_ylim([0, 100])
    self.pageNetwork.panel2.axes.set_yticks(range(0, 101, 10))
    self.pageNetwork.panel2.axes.set_autoscale_on(True)

    self.fileCpu = open('/proc/stat')
    self.cpuInfoLast = self.fileCpu.readline().split()[1:-3]
    self.fileCpu.close()
    self.cpuTotalTimeLast = 0
    for item in self.cpuInfoLast:
      self.cpuTotalTimeLast += int(item)
    self.cpuIdleTimeLast = int(self.cpuInfoLast[3])

    self.diskInfoLast = dict()
    self.diskInfoCurrent = dict()
    self.fileDisk = open('/proc/vmstat')
    lines = self.fileDisk.readlines()
    self.fileDisk.close()
    for line in lines:
      temp = line.split()
      self.diskInfoLast[temp[0]] = int(temp[1])
    self.diskReadLast = self.diskInfoLast['pgpgin']
    self.diskWriteLast = self.diskInfoLast['pgpgout']
      
    self.networkInfoLast = dict()
    self.networkInfoCurrent = dict()
    self.fileNetwork = open('/proc/net/dev')
    lines = self.fileNetwork.readlines()
    self.fileNetwork.close()
    for line in lines[2:]:
      temp = line.split()
      self.networkInfoLast[temp[0][:-1]] = temp[1:]
    self.networkInfoLast.pop('lo')
    self.networkReceiveLast = 0
    self.networkTransmitLast = 0
    for key, value in self.networkInfoLast.items():
      self.networkReceiveLast += int(value[0])
      self.networkTransmitLast += int(value[8])
    '''
    for key, value in self.networkInfoLast.items():
      self.networkReceiveLast += int(value[1-1])
      self.networkTransmitLast += int(value[9-1])
    '''


    self.timer.Start(TIMERLENGTH)

  '''
  def MyOpenFiles(self):
    self.fileCpu = open('/proc/stat')
    self.fileMemory = open('/proc/meminfo')
    self.fileDisk = open('/proc/vmstat')
    self.fileNetwork = open('/proc/net/dev')
  '''

  def MyCreateTimer(self):
    self.timer = wx.Timer(self)
    self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)

  def MyCreateMenuBar(self):
    menuBar = wx.MenuBar()

    menuFile = wx.Menu()
    menuFileItemOpen = menuFile.Append(-1, "&Open...")
    menuFileItemSave = menuFile.Append(-1, "&Save...")
    menuFile.AppendSeparator()
    menuFileItemExit = menuFile.Append(-1, "&Exit")
    self.Bind(wx.EVT_MENU, self.OnOpen, menuFileItemOpen)
    self.Bind(wx.EVT_MENU, self.OnSave, menuFileItemSave)
    self.Bind(wx.EVT_MENU, self.OnExit, menuFileItemExit)
    menuBar.Append(menuFile, "&File")

    menuAction = wx.Menu()
    menuActionItemRecord = menuAction.Append(-1, "&Record")
    menuActionItemStop = menuAction.Append(-1, "S&top")
    menuAction.AppendSeparator()
    menuActionItemPlay = menuAction.Append(-1, "Play")
    menuActionItemPause = menuAction.Append(-1, "&Pause")
    menuActionItemEnd = menuAction.Append(-1, "E&nd")
    self.Bind(wx.EVT_MENU, self.OnRecord, menuActionItemRecord)
    self.Bind(wx.EVT_MENU, self.OnStop, menuActionItemStop)
    self.Bind(wx.EVT_MENU, self.OnPlay, menuActionItemPlay)
    self.Bind(wx.EVT_MENU, self.OnPause, menuActionItemPause)
    self.Bind(wx.EVT_MENU, self.OnEnd, menuActionItemEnd)
    menuBar.Append(menuAction, "&Action")

    menuConfig = wx.Menu()
    menuConfigItem1 = menuConfig.Append(-1, "config1")
    menuConfigItem2 = menuConfig.Append(-1, "config2")
    self.Bind(wx.EVT_MENU, self.OnConfig1, menuConfigItem1)
    self.Bind(wx.EVT_MENU, self.OnConfig2, menuConfigItem2)
    menuBar.Append(menuConfig, "&Configuration")

    menuHelp = wx.Menu()
    menuHelpItemVersion = menuHelp.Append(-1, "&Version")
    menuHelpItemAbout = menuHelp.Append(-1, "&About")
    self.Bind(wx.EVT_MENU, self.OnVersion, menuHelpItemVersion)
    self.Bind(wx.EVT_MENU, self.OnAbout, menuHelpItemAbout)
    menuBar.Append(menuHelp, "&Help")

    self.SetMenuBar(menuBar)


  def MyCreateToolBar(self):
    toolBar = self.CreateToolBar()

    bmpOpen = wx.Image("open.bmp", wx.BITMAP_TYPE_BMP).ConvertToBitmap()
    toolOpen = toolBar.AddSimpleTool(-1, bmpOpen, 'Open', "Open a record file and display it.")
    self.Bind(wx.EVT_MENU, self.OnOpen, toolOpen)

    bmpSave = wx.Image("save.bmp", wx.BITMAP_TYPE_BMP).ConvertToBitmap()
    toolSave = toolBar.AddSimpleTool(-1, bmpSave, 'Save', "Save the data to a record file.")
    self.Bind(wx.EVT_MENU, self.OnSave, toolSave)

    bmpRecord = wx.Image("begin.bmp", wx.BITMAP_TYPE_BMP).ConvertToBitmap()
    toolRecord = toolBar.AddSimpleTool(-1, bmpRecord, 'Record', "Begin recording.")
    self.Bind(wx.EVT_MENU, self.OnRecord, toolRecord)

    bmpStop = wx.Image("begin.bmp", wx.BITMAP_TYPE_BMP).ConvertToBitmap()
    toolStop = toolBar.AddSimpleTool(-1, bmpStop, 'Stop', "Stop recording.")
    self.Bind(wx.EVT_MENU, self.OnStop, toolStop)

    bmpPlay= wx.Image("begin.bmp", wx.BITMAP_TYPE_BMP).ConvertToBitmap()
    toolPlay = toolBar.AddSimpleTool(-1, bmpPlay, 'Play', "Play.")
    self.Bind(wx.EVT_MENU, self.OnPlay, toolPlay)

    bmpPause= wx.Image("pause.bmp", wx.BITMAP_TYPE_BMP).ConvertToBitmap()
    toolPause = toolBar.AddSimpleTool(-1, bmpPause, 'Pause', "Pause")
    self.Bind(wx.EVT_MENU, self.OnPause, toolPause)

    bmpEnd = wx.Image("stop.bmp", wx.BITMAP_TYPE_BMP).ConvertToBitmap()
    toolEnd = toolBar.AddSimpleTool(-1, bmpEnd, 'End', "End")
    self.Bind(wx.EVT_MENU, self.OnEnd, toolEnd)
    
    toolBar.Realize()




  def OnOpen(self, event):
    #pattern =  "Data file(*.pm)|*.pm|"\
               #"All files(*.*)|*.*"
    pattern =  "Data file(*.pm)|*.pm|"
    pathCurrent = os.getcwd()
    dialog = wx.FileDialog(None, "Choose a file", pathCurrent, "", pattern, wx.OPEN)
    if dialog.ShowModal() == wx.ID_OK:
      filename = dialog.GetPath()
      f = open(filename, 'r')
      f.close()
    dialog.Destroy()
    self.openAlready = True

  def OnSave(self, event):
    #pattern =  "Data file(*.pm)|*.pm|"\
               #"All files(*.*)|*.*"
    pattern =  "Data file(*.pm)|*.pm|"
    pathCurrent = os.getcwd()
    dialog = wx.FileDialog(None, "Choose a file", pathCurrent, "", pattern, wx.SAVE|wx.OVERWRITE_PROMPT)
    if dialog.ShowModal() == wx.ID_OK:
      filename = dialog.GetPath()
      if filename[-3:] == '.pm':
        f = open(filename, 'w')
      else:
        f = open(filename+'.pm', 'w')
      f.close()
      os.system('cp ' + pathCurrent + '/Processor.data ' + filename + '.processor')
      os.system('cp ' + pathCurrent + '/Memory.data ' + filename + '.memory')
      os.system('cp ' + pathCurrent + '/Disk.data ' + filename + '.disk')
      os.system('cp ' + pathCurrent + '/Network.data ' + filename + '.network')
    dialog.Destroy()

    
  def OnExit(self, event):
    self.Close(True)

  def OnRecord(self, event):
    self.processorUtilization = [None] * self.length 
    self.memoryUtilization = [None] * self.length 
    self.diskRead = [None] * self.length 
    self.diskWrite = [None] * self.length 
    self.networkReceive = [None] * self.length 
    self.networkTransmit = [None] * self.length 

    self.processorRecordFile.close()
    self.processorRecordFile = open(ProcessorRecordFileName, 'w')
    self.memoryRecordFile = open(MemoryRecordFileName, 'w')
    self.diskRecordFile = open(DiskRecordFileName, 'w')
    self.networkRecordFile = open(NetworkRecordFileName, 'w')
    '''
    selection = self.notebook.GetSelection()
    if selection == 0:
      pass
    elif selection == 1:
      self.ProcessorDraw()
    elif selection == 2:
      self.MemoryDraw()
    elif selection == 3:
      self.DiskDraw()
    elif selection == 4:
      self.NetworkDraw()
      '''




  def OnStop(self, event):
    self.processorRecordFile.close()
    self.memoryRecordFile.close()
    self.diskRecordFile.close()
    self.networkRecordFile.close()

    self.processorUtilization = [None] * self.length 
    self.memoryUtilization = [None] * self.length 
    self.diskRead = [None] * self.length 
    self.diskWrite = [None] * self.length 
    self.networkReceive = [None] * self.length 
    self.networkTransmit = [None] * self.length 

    self.processorRecordFile = open(NullFileName, 'w')
    self.memoryRecordFile = open(NullFileName, 'w')
    self.diskRecordFile = open(NullFileName, 'w')
    self.networkRecordFile = open(NullFileName, 'w')

  def OnPlay(self, event):
    if self.openAlready == False:
      self.OnOpen(event)
    return

  def OnPause(self, event):
    return

  def OnEnd(self, event):
    return

  def OnConfig1(self, event):
    return 

  def OnConfig2(self, event):
    return 

  def OnVersion(self, event):
    dialog = wx.MessageDialog(None, "Version Information", 'Version', wx.OK)
    returnCode = dialog.ShowModal()
    dialog.Destroy()

  def OnAbout(self, event):
    dialog = wx.MessageDialog(None, "About Information", 'About', wx.OK)
    returnCode = dialog.ShowModal()
    dialog.Destroy()

  def ProcessorMonitoring(self):
    '''
    self.cpuTotalTimeLast = 0
    for item in self.cpuInfoLast:
      self.cpuTotalTimeLast += int(item)
    self.cpuIdleTimeLast = int(self.cpuInfoLast[3])
    '''


    self.fileProcessor = open('/proc/stat')
    self.cpuInfoCurrent = self.fileProcessor.readline().split()[1:-3]
    self.fileProcessor.close()
    self.cpuTotalTimeCurrent = 0
    for item in self.cpuInfoCurrent :
      self.cpuTotalTimeCurrent += int(item)
    self.cpuIdleTimeCurrent = int(self.cpuInfoCurrent[3])

    total = self.cpuTotalTimeCurrent - self.cpuTotalTimeLast
    idle = self.cpuIdleTimeCurrent - self.cpuIdleTimeLast
    rate = (total - idle) * 1.0 / total * 100

    self.processorRecordFile.write(str(rate) + '\n')

    self.processorUtilization.pop(0)
    self.processorUtilization.append(rate)

    self.cpuInfoLast = self.cpuInfoCurrent
    self.cpuTotalTimeLast = self.cpuTotalTimeCurrent
    self.cpuIdleTimeLast = self.cpuIdleTimeCurrent

  def ProcessorDraw(self):
    self.pageProcessor.FigureCanvas.restore_region(self.pageProcessor.bg)
    self.dataProcessor.set_ydata(self.processorUtilization)
    self.pageProcessor.axes.draw_artist(self.dataProcessor)
    self.pageProcessor.FigureCanvas.blit(self.pageProcessor.axes.bbox)
    

  def MemoryMonitoring(self):
    self.fileMemory = open('/proc/meminfo')
    memoryTotal = int(self.fileMemory.readline().split()[1])
    memoryFree = int(self.fileMemory.readline().split()[1])
    memoryBuffers = int(self.fileMemory.readline().split()[1])
    memoryCached = int(self.fileMemory.readline().split()[1])

    rate = (memoryTotal-memoryFree-memoryBuffers-memoryCached) * 1.0 / memoryTotal * 100

    self.memoryRecordFile.write(str(rate) + '\n')

    self.memoryUtilization.pop(0)
    self.memoryUtilization.append(rate)

  def MemoryDraw(self):
    self.pageMemory.FigureCanvas.restore_region(self.pageMemory.bg)
    self.dataMemory.set_ydata(self.memoryUtilization)
    self.pageMemory.axes.draw_artist(self.dataMemory)
    self.pageMemory.FigureCanvas.blit(self.pageMemory.axes.bbox)

  def DiskMonitoring(self):
    self.fileDisk = open('/proc/vmstat')
    lines = self.fileDisk.readlines()
    self.fileDisk.close()
    for line in lines:
      temp = line.split()
      self.diskInfoCurrent[temp[0]] = int(temp[1])
    self.diskReadCurrent = self.diskInfoCurrent['pgpgin']
    self.diskWriteCurrent = self.diskInfoCurrent['pgpgout']

    rateRead = (self.diskReadCurrent-self.diskReadLast)*1.0 / (TIMERLENGTH*1.0/1000)
    rateWrite = (self.diskWriteCurrent-self.diskWriteLast)*1.0 / (TIMERLENGTH*1.0/1000) 

    self.diskRecordFile.write(str(rateRead) + '\t' + str(rateWrite) + '\n')

    self.diskRead.pop(0)
    self.diskRead.append(rateRead)
    self.diskWrite.pop(0)
    self.diskWrite.append(rateWrite)

    self.diskInfoLast = self.diskInfoCurrent
    self.diskReadLast = self.diskReadCurrent
    self.diskWriteLast = self.diskWriteCurrent

  def DiskDraw(self):
    self.pageDisk.panel1.axes.set_ylim([0, max(self.diskRead)*1.1])
    self.pageDisk.panel1.FigureCanvas.restore_region(self.pageDisk.panel1.bg)
    self.dataDiskRead.set_ydata(self.diskRead)
    self.pageDisk.panel1.axes.draw_artist(self.dataDiskRead)
    self.pageDisk.panel1.FigureCanvas.blit(self.pageDisk.panel1.axes.bbox)

    self.pageDisk.panel2.axes.set_ylim([0, max(self.diskWrite)*1.1])
    self.pageDisk.panel2.FigureCanvas.restore_region(self.pageDisk.panel2.bg)
    self.dataDiskWrite.set_ydata(self.diskWrite)
    self.pageDisk.panel2.axes.draw_artist(self.dataDiskWrite)
    self.pageDisk.panel2.FigureCanvas.blit(self.pageDisk.panel2.axes.bbox)

  def NetworkMonitoring(self):
    self.fileNetwork = open('/proc/net/dev')
    lines = self.fileNetwork.readlines()
    self.fileNetwork.close()
    for line in lines[2:]:
      temp = line.split()
      self.networkInfoCurrent[temp[0][:-1]] = temp[1:]
    self.networkInfoCurrent.pop('lo')
    self.networkReceiveCurrent = 0
    self.networkTransmitCurrent = 0
    '''
    self.networkReceiveCurrent += int(self.networkInfoCurrent['eth0'][0])
    self.networkTransmitCurrent += int(self.networkInfoCurrent['eth0'][8])
    '''
    for key, value in self.networkInfoCurrent.items():
      self.networkReceiveCurrent += int(value[1-1])
      self.networkTransmitCurrent += int(value[9-1])
  
    rateReceive = (self.networkReceiveCurrent-self.networkReceiveLast)*1.0 / 1024 / 8 / (TIMERLENGTH*1.0/1000) 
    rateTransmit = (self.networkTransmitCurrent-self.networkTransmitLast)*1.0 / 1024 / 8 / (TIMERLENGTH*1.0/1000)

    self.networkRecordFile.write(str(rateReceive) + '\t' + str(rateTransmit) + '\n')

    self.networkReceive.pop(0)
    self.networkReceive.append(rateReceive)
    self.networkTransmit.pop(0)
    self.networkTransmit.append(rateTransmit)

    #print self.networkReceiveLast
    #print self.networkTransmitLast

    self.networkInfoLast = self.networkInfoCurrent
    self.networkReceiveLast = self.networkReceiveCurrent
    self.networkTransmitLast = self.networkTransmitCurrent


  def NetworkDraw(self):
    if((self.networkReceive[-1]-100)*(self.networkReceive[-2]-100) < 0):
      if(self.networkReceive[-1] < 100):
        self.pageNetwork.panel1.axes.set_ylim(0, 100)
        self.pageNetwork.panel1.axes.set_yticks(range(0, 100, 10))
        self.pageNetwork.panel1.UpdatePlot()
      else:
        self.pageNetwork.panel1.axes.set_ylim(0, 1024)
        self.pageNetwork.panel1.axes.set_yticks(range(0, 1024, 100))
        self.pageNetwork.panel1.UpdatePlot()
        
    #self.pageNetwork.panel1.axes.set_autoscale_on(True);
    self.pageNetwork.panel1.FigureCanvas.restore_region(self.pageNetwork.panel1.bg)
    self.dataNetworkReceive.set_ydata(self.networkReceive)
    self.pageNetwork.panel1.axes.draw_artist(self.dataNetworkReceive)
    self.pageNetwork.panel1.FigureCanvas.blit(self.pageNetwork.panel1.axes.bbox)

    if((self.networkTransmit[-1]-100)*(self.networkTransmit[-2]-100) < 0):
      if(self.networkTransmit[-1] < 100):
        self.pageNetwork.panel2.axes.set_ylim(0, 100)
        self.pageNetwork.panel2.axes.set_yticks(range(0, 100, 10))
        self.pageNetwork.panel2.UpdatePlot()
      else:
        self.pageNetwork.panel2.axes.set_ylim(0, 1024)
        self.pageNetwork.panel2.axes.set_yticks(range(0, 1024, 100))
        self.pageNetwork.panel2.UpdatePlot()
        
    #self.pageNetwork.panel2.axes.set_autoscale_on(True);
    self.pageNetwork.panel2.FigureCanvas.restore_region(self.pageNetwork.panel2.bg)
    self.dataNetworkTransmit.set_ydata(self.networkTransmit)
    self.pageNetwork.panel2.axes.draw_artist(self.dataNetworkTransmit)
    self.pageNetwork.panel2.FigureCanvas.blit(self.pageNetwork.panel2.axes.bbox)

  def OnTimer(self, evt):

    self.ProcessorMonitoring()
    self.MemoryMonitoring()
    self.DiskMonitoring()
    self.NetworkMonitoring()

    selection = self.notebook.GetSelection()

    if selection == 0:
      pass
    elif selection == 1:
      self.ProcessorDraw()
    elif selection == 2:
      self.MemoryDraw()
    elif selection == 3:
      self.DiskDraw()
    elif selection == 4:
      self.NetworkDraw()




class App(wx.App):
  
  def OnInit(self):
    frame = MyFrame(parent = None, id = -1)
    frame.Show()
    return True

def main():
  os.system('rm ' + 'Processor.data ')
  os.system('rm ' + 'Memory.data ')
  os.system('rm ' + 'Disk.data ')
  os.system('rm ' + 'Network.data ')
  app = App()
  app.MainLoop()

if __name__ == '__main__':
  main()
