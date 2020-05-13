#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 11:57:02 2020
@author: lkurth
"""

import wx
#import wx.xrc
from file_reader import Txt_Reader
import os,logging,pprint
from pubsub import pub
import jumeg_base_config
import jumeg_base
import jumeg_gui_wxlib_utils_controls
import jumeg_gui_config
from jumeg.base import jumeg_logger
logger = logging.getLogger('jumeg')
logging.basicConfig(level=logging.DEBUG)


class ButtonPanel(wx.Panel):
   def __init__(self,parent):
      wx.Panel.__init__(self,parent,style=wx.BORDER_SUNKEN)
      self._wx_init()
      self._ApplyLayout()
      
   def _wx_init(self):
      self._bt_all = wx.Button(self,label="Select All",name=self.GetName()+".BT.ALL")
      self._bt_print = wx.Button(self,label="Print",name=self.GetName()+".BT.PRINT")
      #self._bt_del = wx.Button(self,label="Delete Selected",name=self.GetName()+".BT.DEL")
      self._bt_clear = wx.Button(self,label="Clear",name=self.GetName()+".BT.CLEAR")
      self._bt_apply = wx.Button(self,label="Apply",name=self.GetName()+".BT.APPLY")
   
   def _ApplyLayout(self):
      HA=wx.ALIGN_CENTER_HORIZONTAL | wx.ALL
      myButtonSizer=wx.BoxSizer(wx.HORIZONTAL)
      myButtonSizer.Add(self._bt_all,0,HA,5)
      myButtonSizer.Add(self._bt_print,0,HA,5)
      #myButtonSizer.Add(self._bt_del,0,HA,5)
      myButtonSizer.Add(self._bt_clear,0,HA,5)
      myButtonSizer.Add((0,0),1,HA,2)
      myButtonSizer.Add(self._bt_apply,0,HA,5)
      self.SetAutoLayout(True)
      self.SetSizer(myButtonSizer)
      self.SetBackgroundColour("blue")
      self.Fit()
      self.Layout()
      
class LbBtPanel(wx.Panel):
   def __init__(self,parent,fname):
      wx.Panel.__init__(self,parent,style=wx.BORDER_SUNKEN)
      pub.subscribe(self.my_listener,"listBoxListener")
      self._wx_init(fname)
      self._ApplyLayout()
      
   def _wx_init(self,fname):
      self.reader=Txt_Reader()
      if os.path.exists(fname):
          choices = self.reader.read_file(fname)
      else:
          choices = list()
      self.mListBox=None
      self.Bind(wx.EVT_BUTTON,self.ClickOnButton)
      self.Bind(wx.EVT_LISTBOX,self.select)
      self.Bind(wx.EVT_MOTION,self.OnMouseMove)
      self.counter=0
      self.selectedItems=list()
      self.counter_text=wx.StaticText(self, wx.ID_ANY,(str)(self.counter)+"/0",wx.Point(-1,-1),wx.DefaultSize,0)
      if len(choices)>0:
          self.mListBox = wx.ListBox(self,wx.ID_ANY,choices=choices,style=wx.LB_MULTIPLE) 
          self.mListBox.SetFont(wx.Font(12,75,90,90,False,wx.EmptyString))
          self.mListBox.SetToolTip("ListBox")
          self.btPanel=ButtonPanel(self)
      else:
          fname=self.frame.OnOpen()
          choices=self.reader.read_file(fname)
          self.updateChoices(choices)
      self.update_counter_text()
      
   def _ApplyLayout(self):
       self.counter_text.SetForegroundColour('red')
       myListBoxSizer=wx.BoxSizer(wx.VERTICAL)
       myListBoxSizer.Add(self.counter_text,0,wx.ALIGN_CENTER_HORIZONTAL | wx.EXPAND | wx.ALL,5)
       myListBoxSizer.Add(self.mListBox,1,wx.ALIGN_CENTER_HORIZONTAL | wx.EXPAND | wx.ALL,5)
       myListBoxSizer.Add(self.btPanel,0,wx.ALIGN_CENTER_HORIZONTAL | wx.ALL | wx.EXPAND,5)
       self.SetAutoLayout(True)
       self.SetSizer(myListBoxSizer)
       self.Fit()
       self.Layout()
   
   def my_listener(self,message,arg2=None):
       if message=="update":
            self.deleteAll()
            choices=self.reader.read_file(arg2)
            self.updateChoices(choices)
            #self.mListBox.InsertItems(items=self.reader.read_file(file),pos=0)
            self.update_counter_text()
            self.mListBox.Bind(wx.EVT_LISTBOX,self.select)
            self.mListBox.Bind(wx.EVT_MOTION,self.OnMouseMove)
            
   def GetSelectedFiles(self):
       return [self.reader._file_list[i] for i in self.selectedItems]
   
   def ClickOnButton(self,event):
      obj=event.GetEventObject()
      if obj.GetLabel()=="Select All":
         self.selectAll()
      elif obj.GetLabel()=="Deselect All":
         self.deselectAll()
      elif obj.GetName().endswith(".BT.PRINT"):
         """for i in self.selectedItems:
            print(self.reader._file_list[i])"""
         #print(self.GetSelectedFiles())
         logger.info("SELECTED FIles in ListBox: {} ".format(pprint.pformat( self.GetSelectedFiles(),indent=4) ) )
      elif obj.GetName().endswith(".BT.DEL"):
         self.deleteSelectedItems()
      elif obj.GetName().endswith("BT.CLEAR"):
         self.deleteAll()
      elif obj.GetName().endswith("BT.APPLY"):
         pub.sendMessage("tree_listener", message="apply",arg2="intext_config.yaml")
         
   def select(self,event):
        """Simulate CTRL-click on ListBox"""
        selection = self.mListBox.GetSelections()
        for i in selection:
            if i not in self.selectedItems:
                # add to list of selected items
                self.selectedItems.append(i)
                self.mListBox.Select(i)
                self.counter+=1
            elif len(selection) == 1:
                # remove from list of selected items
                self.selectedItems.remove(i)
                self.mListBox.Deselect(i)
                self.counter-=1
    
        for i in self.selectedItems:
            # actually select all the items in the list
            self.mListBox.Select(i)
            
        if len(self.selectedItems)==len(self.reader._file_list):
            self.btPanel._bt_all.SetLabel("Deselect All")
        else:
            self.btPanel._bt_all.SetLabel("Select All")
        self.update_counter_text()
        
        
   def selectAll(self):
      for i in range(len(self.reader._file_list)):
         self.mListBox.SetSelection(i)
         self.selectedItems.append(i)
      self.btPanel._bt_all.SetLabel("Deselect All")
      self.counter=len(self.reader._file_list)
      self.update_counter_text()
   
   def deselectAll(self):
      for i in self.mListBox.GetSelections():
         self.mListBox.Deselect(i)
      self.selectedItems.clear()
      self.btPanel._bt_all.SetLabel("Select All")
      self.counter=0
      self.update_counter_text()
      
   def deleteSelectedItems(self):
      if len(self.selectedItems)==0:
         pass
      else:
         selection=self.mListBox.GetSelections()
         selection.sort(reverse=True)
         for i in selection:
            self.mListBox.Delete(i)
            self.reader._file_list.pop(i)
         self.deselectAll()
         
   def deleteAll(self):
      self.mListBox.Clear()
      self.counter=0
      self.counter_text.SetLabel((str)(self.counter)+"/0")
      self.mListBox.SetToolTip("")
         
   def update_counter_text(self):
      self._maxFiles=len(self.reader._file_list)
      self.counter_text.SetLabel((str)(self.counter)+"/"+(str)(self._maxFiles))
   
   @property
   def frame(self):
      return self.GetParent().GetParent()
  
   def OnMouseMove(self, event):
        # Event handler for mouse move event. Updates current position of cursor in data coordinates.
        
        event.Skip()
        # get mouse position in window
        self.mousePos = self.ScreenToClient(wx.GetMousePosition())
        x, y = self.mousePos.Get()
        if self.mListBox.HitTest(x,y)!=wx.NOT_FOUND and len(self.reader._file_list)>1:
         self.mListBox.SetToolTip(self.reader._file_list[self.mListBox.HitTest(x,y)-1])
   
   def updateChoices(self,choices):
      if self.mListBox:
          self.mListBox.Clear()
          self.mListBox.AppendItems(choices)
      else:
          myListBoxSizer=wx.BoxSizer(wx.VERTICAL)
          myListBoxSizer.Add(self.counter_text,1,wx.ALIGN_CENTER_HORIZONTAL | wx.EXPAND | wx.ALL,5)
          self.mListBox = wx.ListBox(self,wx.ID_ANY,choices=choices,style=wx.LB_MULTIPLE) 
          self.mListBox.SetFont(wx.Font(12,75,90,90,False,wx.EmptyString))
          self.mListBox.SetToolTip("ListBox")
          myListBoxSizer.Add(self.mListBox,1,wx.ALIGN_CENTER_HORIZONTAL | wx.EXPAND | wx.ALL,5)
          self.btPanel=ButtonPanel(self)
          myListBoxSizer.Add(self.btPanel,0,wx.ALIGN_CENTER_HORIZONTAL | wx.ALL | wx.EXPAND,5)
          self.SetSizer(myListBoxSizer)
      self.selectAll()
      self.deselectAll()
      
class TreeCtrlPanel(wx.Panel):
    def __init__(self,parent):
      wx.Panel.__init__(self,parent)
      pub.subscribe(self.my_listener,"tree_listener")
      self._wx_init()
      self._ApplyLayout()
      
    def _wx_init(self):
      self._TreePanel=jumeg_gui_config.CtrlPanel(self,fname="")
      self._TreePanel.Hide()
      
    def _ApplyLayout(self):
      myTreeSizer=wx.BoxSizer(wx.VERTICAL)
      myTreeSizer.Add(self._TreePanel,1,wx.ALIGN_CENTER_HORIZONTAL | wx.EXPAND | wx.ALL,5)
      self.SetAutoLayout(True)
      self.SetSizer(myTreeSizer)
      self.Fit()
      self.Layout()
      
    def my_listener(self,message,arg2=None):
       if message=="apply" and arg2:
           #self._TreePanel=jumeg_gui_config.CtrlPanel(self.Splitter,fname="intext_config.yaml")
           #os.system('python jumeg_gui_config.py &')
           self._TreePanel._init_cfg(config=arg2)
           self._TreePanel.Show()
           self._TreePanel.Layout()
           self.Layout()
       elif message=="load_cfg":
           self._TreePanel.ClickOnOpenConfigFile()
           if self._TreePanel.IsShown()==False:
               self._TreePanel.Show(True)
               self._TreePanel.Show()
               self._TreePanel.Layout()
               self.Layout()
       elif message=="save_cfg":
           if self._TreePanel.IsShown():
               self._TreePanel.ClickOnSaveConfigFile()
           else:
               logger.info("No Config dict to save")
           
      
class MyApp(wx.App):
   def OnInit(self):
      self.frame=MyFrame(None)
      self.SetTopWindow(self.frame)
      self.frame.Show()
      return True
   
class MyFrame(wx.Frame):
   def __init__(self,parent,fname=None):
      wx.Frame.__init__(self,parent,id=wx.ID_ANY,title="JuMEG ListBox",pos=wx.DefaultPosition, size=wx.Size(500,400),style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)
      self._wx_init(fname)
      self._ApplyLayout()
      
   def _wx_init(self,fname):
      if not fname:
          fname="intext_meeg_filelist.txt"
          #fname=""
      
      self.Splitter=wx.SplitterWindow(self)
      
      self._LbBtPanel=LbBtPanel(self.Splitter,fname)
      
      #self._LbBtPanel.Bind(wx.EVT_BUTTON,self.ClickOnButton)
      
      self._TreePanel=TreeCtrlPanel(self.Splitter)
      
      self.Splitter.SplitVertically(self._LbBtPanel,self._TreePanel)
      self.Splitter.SetSashGravity(0.5)
      
      self.init_menu()
      
      #self._maxFiles=len(self.reader._file_list) 
      
      self.headerLabel = wx.StaticText(self, wx.ID_ANY,"JuMEG ListBox",wx.Point(-1,-1),wx.DefaultSize,0)
      self.headerLabel.Wrap(-1)
      self.headerLabel.SetFont(wx.Font(wx.NORMAL_FONT.GetPointSize(),75,90,92,True,wx.EmptyString))
      
   def _ApplyLayout(self):
      myBoxGridSizer=wx.BoxSizer(wx.VERTICAL)
      
      myBoxGridSizer.Add(self.headerLabel,0,wx.ALL | wx.ALIGN_CENTER_HORIZONTAL,5)
      myBoxGridSizer.Add(self.Splitter,1,wx.ALL | wx.EXPAND,5)
      self.SetSizer(myBoxGridSizer)
      self.SetAutoLayout(True)
      self.Layout()
      self.Fit()
      self.Layout()
      
      self.Centre(wx.BOTH)
      
   def init_menu(self):
      self._menubar=wx.MenuBar()
      open_menu=wx.Menu()
      
      load_file_list=wx.MenuItem(open_menu,id=1,text="load File List",kind=wx.ITEM_NORMAL)
      open_menu.Append(load_file_list)
      
      save_file_list=wx.MenuItem(open_menu,id=2,text="save As File List",kind=wx.ITEM_NORMAL)
      open_menu.Append(save_file_list)
      
      load_config=wx.MenuItem(open_menu,id=3,text="load Config File",kind=wx.ITEM_NORMAL)
      open_menu.Append(load_config)
      
      save_config=wx.MenuItem(open_menu,id=4,text="save As Config File",kind=wx.ITEM_NORMAL)
      open_menu.Append(save_config)
      
      separator_item=wx.MenuItem(open_menu,id=5,text="separator",kind=wx.ITEM_NORMAL)
      open_menu.Append(separator_item)
      
      exit_item=wx.MenuItem(open_menu,id=6,text="exit",kind=wx.ITEM_NORMAL)
      open_menu.Append(exit_item)
      
      self._menubar.Append(open_menu, 'Menu')
      self.SetMenuBar(self._menubar)
      self.Bind(wx.EVT_MENU,self.menuhandler)
    
   @property
   def mListBox(self):
       return self._LbBtPanel.mListBox
   
   @property
   def bt_all(self):
       return self._LbBtPanel.btPanel._bt_all
    
   def menuhandler(self,event):
      id=event.GetId()
      if id==1:
         file=self.OnOpen()
         if file:
            pub.sendMessage("listBoxListener",message="update",arg2=file)
      elif id==2:
          pass
      elif id==3:
          pub.sendMessage("tree_listener",message="load_cfg")
      elif id==4:
          pub.sendMessage("tree_listener",message="save_cfg")
      elif id==5:
          id=self._menubar.FindMenu("Menu")
          self._menubar.GetMenu(id).AppendSeparator()
      elif id==6:
          self.Close()
         
   def OnOpen(self, event=None):
       '''
       opens a dialogue to load a .txt file and build a ListBox out of it
       '''
       # otherwise ask the user what new file to open
       with wx.FileDialog(self, "Open txt file", wildcard="txt file (*.txt)|*.txt",
                          style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
           
           #fileDialog.SetDirectory(os.path.dirname(self.cfg.filename))
           if fileDialog.ShowModal() == wx.ID_CANCEL:
               return     # the user changed their mind
   
           # Proceed loading the file chosen by the user
           pathname = fileDialog.GetPath()
           try:
              if os.path.isfile(pathname):
                  return pathname
           except IOError:
               wx.LogError("Cannot open file '%s'." % pathname)
           return None
      
      
if __name__ == "__main__":
   app=MyApp(False)
   app.MainLoop()