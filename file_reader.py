#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 09:24:01 2020
@author: lkurth
"""

import os
from pubsub import pub
class FileList():
   
   def __init__(self):
      self._file_list=list()
      self._init_pubsub()
      
   @property
   def files(self): return self._file_list
   
   @property
   def counts(self): return len(self._file_list)
   
   def _init_pubsub(self):
       pass
   
   def read_lines(self, f):
      self._file_list=list()
      for line in f:
         line=f.readline().strip()
         if line.startswith("#"): continue
         self._file_list.append(line)
      return self._file_list
         
   def read_file(self, fname):
      self._file_list=list()
      files=list()
      if fname:
          if os.path.exists(fname):
              with open(fname,"r") as f:
                 self.read_lines(f)
              files=self.get_all_basenames()
      pub.sendMessage("listBoxListener",message="update",arg2=files)
      print(files)
      return files
   
   def get_all_basenames(self):
      index=range(len(self._file_list))
      self.get_basenames(index)

   def get_basenames(self,index=None):
       if isinstance(index,list):
          print("test1")
          return [os.path.basename(self._file_list[i]) for i in index]
       elif isinstance(index,int):
          print("test2")
          return os.path.basename(self._file_list[index])
       else:
          print("test3")
          print(type(self._file_list))
          return self._file_list
      
   def get_files(self, index):
      if isinstance(index,list):
         return [self._file_list[i] for i in index]
      elif isinstance(index,int):
         return self._file_list[index]
      else:
         return None
      
   def remove_file(self,index):
      self._file_list.pop(index)
      
   def clear(self):
       self._file_list=list()
      

if __name__=="__main__":        
   reader=FileList()
   f=reader.read_file("intext_meeg_filelist.txt")    
   print(f)