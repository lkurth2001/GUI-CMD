#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 09:24:01 2020
@author: lkurth
"""
import os
from pubsub import pub
import getpass
import jumeg_base_config

___version__ = "2020-05-26-001"

class FileList():
   
   def __init__(self):
      self._file_list = list()
      self._name      = "FILE_LIST"
      self._init_pubsub()
   
   @property
   def name(self): return self._name
   
   @property
   def files(self): return self._file_list
   
   @property
   def counts(self): return len(self._file_list)
   @property
   def n_files(self): return len(self._file_list)
   
   def _init_pubsub(self):
       pass
      
       
   def _read_lines(self, f):
      self._file_list=list()
      for line in f:
         line = f.readline().strip()
         if line.startswith("#"): continue
         self._file_list.append(line)
        
      return self._file_list
         
   def read_file(self,fname):
    
      self.clear()
      
      if fname:
         if os.path.exists(fname):
            with open(fname,"r") as f:
                 self._read_lines(f)
    
      pub.sendMessage(self._name,data=self.get_basenames() ) 
      
      return self._file_list
   
   def write_tmp_files(self,fdata=list(),cdata=dict()):
      CFG=jumeg_base_config.JuMEG_CONFIG()
      user=getpass.getuser()
      count=1
      num=str(count).zfill(3)
      ffname="test_file_"+user+"_"+num+".txt"
      cfname="test_config_"+user+"_"+num+".yaml"
      while os.path.exists(ffname) or os.path.exists(cfname):
         count+=1
         num=str(count).zfill(3)
         ffname="test_file_"+user+"_"+num+".txt"
         cfname="test_config_"+user+"_"+num+".yaml"
      with open(ffname,"w") as f:
         f.writelines("%s\n" % line for line in fdata)
      CFG.save_cfg(fname=cfname,data=cdata)
      print(ffname)
      print(cfname)
  
   
   def get_basenames(self,index=None):
       
       if isinstance(index,list):
         return [ os.path.basename( self._file_list[i] ) for i in index]
       elif isinstance(index,int):
         return os.path.basename( self._file_list[index] )
       else:
         return [ os.path.basename( self._file_list[i] ) for i in range( self.counts ) ]
       
   
   def get_files(self, index):
      if isinstance(index,list):
         return [self._file_list[i] for i in index]
      elif isinstance(index,int):
         return self._file_list[index]
      else:
         return self._files
      
   
   def remove_file(self,index):
      self._file_list.pop(index)

   def clear(self):
       self._file_list = []
       

if __name__=="__main__":        
   reader = FileList()
   f=reader.read_file("intext_meeg_filelist.txt")    
   print(f)