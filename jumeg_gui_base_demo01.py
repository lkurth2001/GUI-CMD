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

from pubsub         import pub
from file_IO import FileList
import jumeg_gui_config

import logging,pprint
import jumeg_base_config
import jumeg_base
import jumeg_gui_wxlib_utils_controls
import jumeg_gui_config
from jumeg.base import jumeg_logger
logger = logging.getLogger('jumeg')
logging.basicConfig(level=logging.DEBUG)

__version__="2020-05-26-001"


def ShowFileDLG(self):
    '''
    opens a dialogue to load a .txt file and build a ListBox out of it
    '''
    # otherwise ask the user what new file to open
    pathname = None
    with wx.FileDialog(self, "Open txt file", wildcard="txt file (*.txt)|*.txt",
                       style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
        
    #fileDialog.SetDirectory(os.path.dirname(self.cfg.filename))
         if fileDialog.ShowModal() == wx.ID_CANCEL:
            return 
         pathname = fileDialog.GetPath()
         if not os.path.isfile(pathname):
            wx.LogError("Cannot open file '%s'." % pathname)
            pathname = None
                   
    return pathname
 
def OnSaveAs(self):
        with wx.FileDialog(self, "Save txt file", wildcard="txt files (*.txt)|*.txt",
                          style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
             fileDialog.SetDirectory(os.getcwd())
             if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind
   
           # save the current contents in the file
             pathname = fileDialog.GetPath()
             if not pathname.endswith(".yaml"):
                pathname+=".yaml"
             try:
                 #data = self._CfgTreeCtrl._used_dict
                 print(pathname)
                 #self.cfg.save_cfg(fname=pathname,data=data)
             except IOError:
                 wx.LogError("Cannot save current data in file '%s'." % pathname)


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
   """
    BT= ButtonPanel(self,name="BUTTON",labels=["De/Select","Info","TEST","Cancel","Apply"])
    BT.BindCtrls( ClickOnButton )
   """
      
   @property
   def labels(self): return self._labels
   
   def _init(self,**kwargs):
       self._labels = kwargs.get("labels",["Apply"])
       self.SetName( kwargs.get("name",self.GetName()) )
       self._bts    = []
       
   def _wx_init(self,**kwrgs):
       for label in self._labels:
          self._bts.append( wx.Button(self,label=label,name=self.GetName()+"."+label.upper()))
       self.Bind(wx.EVT_BUTTON,self.ClickOnCtrl)
      
   def ClickOnCtrl(self,evt):
       obj  = evt.GetEventObject()
       data = obj.GetName().upper()
       #print("--> ClickOnCtr send pubsub call: "+ data)
       pub.sendMessage( obj.GetName().upper(),data=data )
       
   def _ApplyLayout(self):
      LA = wx.LEFT|wx.ALL
      #hbox = wx.ALIGN_CENTER_HORIZONTAL | wx.ALL
      hbox = wx.BoxSizer(wx.HORIZONTAL)
      for bt in self._bts:
          hbox.Add(bt,0,LA,5)
          #hbox.AddStretchSpacer(1)
      self.SetSizer(hbox)
  
   def BindCtrls(self,funct):
       for l in self.labels:
           pub.subscribe(funct,self.GetName()+"."+ l.upper() )
       
 
      
class FileSelectionBox(_BASE):
  
   def _init(self,**kwargs):
             
       self._FileReader = FileList()
     
       self._FLB = None
       self._FSC = None
       self._BUT = None
       
   @property
   def FileSelectionBox(self): return self._FLB
   
   def update_files(self,fname):
       self._FileReader.read_file(fname) 
   
   def _wx_init(self,**kwargs):
     
     #-- file selection counter
      self._FSC = wx.StaticText(self, wx.ID_ANY,style=wx.ALIGN_RIGHT)
      self._FSC.SetForegroundColour('red')
     #-- FileListBox
      self._FLB = wx.ListBox(self,wx.ID_ANY,choices=[],style=wx.LB_MULTIPLE) 
      self._FLB.SetFont(wx.Font(12,75,90,90,False,wx.EmptyString))
      self._FLB.Bind(wx.EVT_MOTION,self.OnMouseMove)
      
      self.Bind(wx.EVT_LISTBOX,self.ClickOnSelect) 
      self._update_file_selection_counter()
      
   def _update_file_selection_counter(self):
       v = "{} / {}".format( len(self._FLB.GetSelections() ) , self._FLB.GetCount() )
       self._FSC.SetLabel( v  )
       
   def ClickOnSelect(self,evt):
       self._update_file_selection_counter()
       
   def update(self,data=None):
       self._FLB.Clear()
       if data:
          self._FLB.AppendItems(data)
       self._update_file_selection_counter()   
    
   def OnMouseMove(self, event):
        # Event handler for mouse move event. Updates current position of cursor in data coordinates.
        
        # get mouse position in window
        x=event.GetX()
        y=event.GetY()
        item=self._FLB.HitTest((x,y))
        if item == wx.NOT_FOUND:
           v=""
        else:
           v=self._FileReader.get_files(item)
        self._FLB.SetToolTip(v)
     
   def _ApplyLayout(self):
       d   = 5
       LEA = wx.ALIGN_LEFT | wx.EXPAND | wx.ALL
      
       vbox = wx.BoxSizer(wx.VERTICAL)
       vbox.Add(self._FSC,0,LEA,d)
       vbox.Add(self._FLB,1,LEA,d)
       self.SetSizer(vbox)
      
   
   def _init_pubsub(self):
       pub.subscribe(self.update,self._FileReader.name)
       pub.subscribe(self.ClickOnOpenFile,"MSG.OPEN_FILE")
       pub.subscribe(self.DeSelectFiles,"BUTTON.DE/SELECT")      
       
   def GetSelectedFiles(self):
       f = self._FileReader.get_files( self._FLB.GetSelections() )
       return f
   
   def DeSelectFiles(self,data):
       if self._FLB.GetSelections():
          for i in self._FLB.GetSelections():
              self._FLB.Deselect(i)
       else:
          for i in range( self._FLB.GetCount() ):
              self._FLB.SetSelection(i)
       self._update_file_selection_counter()
    
              
   def ClickOnOpenFile(self):
       f = ShowFileDLG(self)
       if f:
          self._FileReader.read_file(f) 
   

class ConfigCtrl(_BASE):
      
    def _wx_init(self):
      self._CFG = jumeg_gui_config.CtrlPanel(self,fname="")
      
    def _ApplyLayout(self):
        vbox=wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self._CFG,1,wx.ALIGN_CENTER_HORIZONTAL | wx.EXPAND | wx.ALL,5)
        self.SetSizer(vbox)
     
    
    def _init_pubsub(self):
        pub.subscribe(self.my_listener,"MSG.CONFIG")
      
       
    def my_listener(self,message,arg2=None):
       if message=="apply" and arg2:
           self._CCFG._init_cfg(config=arg2)
           self._CFG.Show()
           self._CFG.Layout()
           self.Layout()
       elif message=="load_cfg":
           self._CFG.ClickOnOpenConfigFile()
           if self._CFG.IsShown()==False:
               self._CFG.Show(True)
               self._CFG.Show()
               self._CFG.Layout()
               self.Layout()
       elif message=="save_cfg":
           if self._CFG.IsShown():
               self._CFG.ClickOnSaveConfigFile()
           else:
               print("No Config dict to save")
           
      
        
class MainPanel(_BASE):
  
    def _init_pubsub(self):
        self._BUT.BindCtrls(self.ClickOnButton)
       
       
    def _wx_init(self,**kwargs):
        self._SPW = wx.SplitterWindow(self)
        self._FSB = FileSelectionBox(self._SPW)
        self._BUT = ButtonPanel(self,name="BUTTON",labels=["Close","De/Select","Info","TEST","Cancel","Apply"])
        
        self._ConfigCtrl = ConfigCtrl(self._SPW)
        
        self._SPW.SplitVertically(self._FSB,self._ConfigCtrl)
        self._SPW.SetSashGravity(0.5)
        
        
    def _ApplyLayout(self):
        ds1 = 2
        LEA = wx.ALIGN_LEFT | wx.EXPAND | wx.ALL
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self._SPW,1,LEA,ds1)
        vbox.Add(self._BUT,0,LEA,ds1)
        
        self.SetSizer(vbox)
  
    def ClickOnButton(self,data=None):
        if data.upper().endswith("APPLY"):
           logger.info("test1")
           if self._FSB and self._ConfigCtrl._CFG._CfgTreeCtrl:
              logger.info("test2")
              if self._FSB.GetSelectedFiles() and self._ConfigCtrl._CFG._CfgTreeCtrl.GetData():
                 logger.info("test3")
                 files=self._FSB.GetSelectedFiles()
                 self._FSB._FileReader.write_tmp_files(fdata=files,cdata=self._ConfigCtrl._CFG._CfgTreeCtrl.GetData())
        
        if data.upper().endswith("DE/Select"):
           self._FSB.DeSelectFiles()    
           
        if data.upper().endswith("INFO"):
           logger.info(self._FSB.GetSelectedFiles())
    
      
        
class MainWindow(wx.Frame):
    def __init__(self,parent,title,**kwargs):
        wx.Frame.__init__(self,parent,-1,title=title)
        self._wx_init(**kwargs)
        
        pub.subscribe(self.ClickOnClose,"BUTTON.CLOSE")
    
    def _wx_init(self,**kwargs):
        w,h = wx.GetDisplaySize()
        self.SetSize(w / 4.0,h / 3.0)
        self.Center()
        self._PNL = MainPanel(self,**kwargs)
        self.init_menu()
   
    def init_menu(self):
      self._menubar=wx.MenuBar()
      open_menu=wx.Menu()
      
      load_file_list=wx.MenuItem(open_menu,id=1,text="load File List",kind=wx.ITEM_NORMAL)
      open_menu.Append(load_file_list)
      
      save_file_list=wx.MenuItem(open_menu,id=2,text="save As File List",kind=wx.ITEM_NORMAL)
      open_menu.Append(save_file_list)
      
      open_menu.AppendSeparator()
      
      load_config=wx.MenuItem(open_menu,id=3,text="load Config File",kind=wx.ITEM_NORMAL)
      open_menu.Append(load_config)
      
      save_config=wx.MenuItem(open_menu,id=4,text="save As Config File",kind=wx.ITEM_NORMAL)
      open_menu.Append(save_config)
      
      open_menu.AppendSeparator()
      
      exit_item=wx.MenuItem(open_menu,id=5,text="Exit",kind=wx.ITEM_NORMAL)
      open_menu.Append(exit_item)
      
      self._menubar.Append(open_menu, 'File I/O')
      self.SetMenuBar(self._menubar)
      self.Bind(wx.EVT_MENU,self.menuhandler)
    
      
    def menuhandler(self,event):
        id=event.GetId()
        if id==1:
           pub.sendMessage("MSG.OPEN_FILE")
        elif id==2:
            OnSaveAs(self)
        elif id==3:
            pub.sendMessage("MSG.CONFIG",message="load_cfg")
        elif id==4:
            pub.sendMessage("MSG.CONFIG",message="save_cfg")
        elif id==5:
            self.ClickOnClose()
            
    def ClickOnClose(self,**data):
        if wx.MessageBox('Close Application?', 'Warning', wx.OK | wx.CANCEL) == wx.OK:
           self.Close()
   
    
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
