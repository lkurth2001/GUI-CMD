#!/usr/bin/env python3
# -+-coding: utf-8 -+-

"""
"""

#--------------------------------------------
# Authors: Frank Boers <f.boers@fz-juelich.de> 
#
#-------------------------------------------- 
# Date: 19.05.20
#-------------------------------------------- 
# License: BSD (3-clause)
#--------------------------------------------
# Updates
#--------------------------------------------
import os
import wx

from pubsub import pub

__version__="2020-05-19-001"

class _BASE(wx.Panel):
   def __init__(self,parent,**kwargs):
      super().__init__(parent,style=wx.BORDER_SUNKEN)
      
      self.SetBackgroundColour( kwargs.get("bg","grey70") ) 
      self._init(**kwargs)
     
      self._wx_init(**kwargs)
      self._ApplyLayout()
      self._ApplyFinalLayout()
      self._init_pubsub()
   
   def _init(self,**kwargs):
       pass   
   
   def _wx_init(self,**kwargs):
       pass
      
   def ClickOnCtrl(self,evt):
       evt.Skip()
       
   def _ApplyLayout(self):
       """
       pack ctrls in sizer and set sizer
    
       Example
       --------    
       hbox = wx.BoxSizer(wx.HORIZONTAL)
       hbox.Add(0,0,1,LA,5)
       self.SetSizer(hbox)
       
       Returns
       -------
       None.

       """
       pass
     
        
   def _ApplyFinalLayout(self):
   
       self.SetAutoLayout(True)
       self.Fit()
       self.Layout()
          
   def _init_pubsub(self):
      pass
    

class ButtonPanel(_BASE):
      
   @property
   def labels(self): return self._labels
   
   def _init(self,**kwargs):
       self._labels = kwargs.get("labels",["Apply"])
       self.SetName( kwargs.get("name",self.GetName()) )
       self._bts    = []
       
   def _wx_init(self):
       for label in self._labels:
          self._bts.append( wx.Button(self,label=label,name=self.GetName()+"."+label.upper()))
       self.Bind(wx.EVT_BUTTON,self.ClickOnCtrl)
      
   def ClickOnCtrl(self,evt):
       obj  = evt.GetEventObject()
       data = obj.GetName().upper()
       print("--> ClickOnCtr send pubsub call: "+ data)
       pub.sendMessage( obj.GetName().upper(),data=data )
       
   def _ApplyLayout(self):
      LA = wx.LEFT|wx.ALL
      #hbox = wx.ALIGN_CENTER_HORIZONTAL | wx.ALL
      hbox = wx.BoxSizer(wx.HORIZONTAL)
      for bt in self._bts:
          hbox.Add(bt,0,LA,5)
          #hbox.AddStretchSpacer(1)
      self.SetSizer(hbox)
     
 
        
        
class MainPanel(_BASE):
  
    def _init_pubsub(self):
        for l in self._BT.labels:
            pub.subscribe(self.show_text,self._BT.GetName()+"."+ l.upper() )
       
    def _wx_init(self,**kwargs):
        self._TXT = wx.TextCtrl(self,id=-1,value="TEST WAS",style=wx.TE_MULTILINE,name="TXT")
        self._BT  = ButtonPanel(self,name="BUTTON",labels=["De/Select","Info","TEST","Cancel","Apply"])
        
    def _ApplyLayout(self):
        ds1 = 10
        LEA = wx.ALIGN_LEFT | wx.EXPAND | wx.ALL
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(wx.StaticLine(self,-1),0,LEA,ds1)
        vbox.Add(self._TXT,0,LEA,ds1)
        vbox.Add(wx.StaticLine(self,-1),0,LEA,ds1)
        vbox.Add(self._BT,0,LEA,ds1)
       
        self.SetSizer(vbox)
    
    def show_text(self,data):
        self._TXT.SetValue(data)
  
        
class MainWindow(wx.Frame):
    def __init__(self,parent,title,**kwargs):
        wx.Frame.__init__(self,parent,-1,title=title)
        self._wx_init(**kwargs)
    
    def _wx_init(self,**kwargs):
        w,h = wx.GetDisplaySize()
        self.SetSize(w / 4.0,h / 3.0)
        self.Center()
        self._PNL = MainPanel(self,**kwargs)
        
   
#=========================================================================================
#==== MAIN
#=========================================================================================
if __name__ == "__main__":
   app = wx.App()
   
   # find | grep DC-raw.fif
   
   s="""./211044/INTEXT01/180226_1013/3/211044_INTEXT01_180226_1013_3_c,rfDC-raw.fif
        ./211044/INTEXT01/180226_1013/4/211044_INTEXT01_180226_1013_4_c,rfDC-raw.fif
        ./211044/INTEXT01/180226_1013/6/211044_INTEXT01_180226_1013_6_c,rfDC-raw.fif
        ./211044/INTEXT01/180226_1013/2/211044_INTEXT01_180226_1013_2_c,rfDC-raw.fif
        ./211044/INTEXT01/180226_1013/5/211044_INTEXT01_180226_1013_5_c,rfDC-raw.fif
        ./211044/INTEXT01/180226_1118/1/211044_INTEXT01_180226_1118_1_c,rfDC-raw.fif
        ./211044/INTEXT01/180226_1118/2/211044_INTEXT01_180226_1118_2_c,rfDC-raw.fif
        ./212842/INTEXT01/190430_1105/1/212842_INTEXT01_190430_1105_1_c,rfDC-raw.fif
        ./212842/INTEXT01/190430_1105/2/212842_INTEXT01_190430_1105_2_c,rfDC-raw.fif
        ./212842/INTEXT01/190430_1001/1/212842_INTEXT01_190430_1001_1_c,rfDC-raw.fif
        ./212842/INTEXT01/190430_1001/3/212842_INTEXT01_190430_1001_3_c,rfDC-raw.fif
        ./212842/INTEXT01/190430_1001/4/212842_INTEXT01_190430_1001_4_c,rfDC-raw.fif
        ./212842/INTEXT01/190430_1001/6/212842_INTEXT01_190430_1001_6_c,rfDC-raw.fif
     """
   flist = [ x.strip()  for x in  s.splitlines() ]
   
   frame = MainWindow(None,'JuMEG File Selection Box',flist=flist)
   frame.Show()
   app.MainLoop()
