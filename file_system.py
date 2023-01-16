import os
from tkinter import *
import shutil as sh
from pathlib import Path
import math

from dataSekura_exceptions import ExistingBackupException, PermissionDeniedException
class File_System_Dealer:
   def __init__(self):
      return
   
   def check_VC_integrity(self):
      if os.path.isdir("C:/Program Files/VeraCrypt") and os.path.isfile("C:/Program Files/VeraCrypt/VeraCrypt Format.exe"):
         return "C:/Program Files/VeraCrypt"
      else:
         return ""
   
   def check_SSFEnc_integrity(self):
      #Now the checking is more exhaustive
      if os.path.isfile("ssefenc.jar"):
         return os.getcwd()
      else:
         return ""
   
   def directory_backup_create(self,path):
      str_ext = "(AUX)"
      if os.path.isdir(path+str_ext) == False:
         sh.copytree(path,path+str_ext)
         return path+str_ext
      else:
         return 0

   
   def file_backup_creation(self, path):
      dest = self.remove_file_extension(path)
      str_ext = "(AUX).bin"
      dest = dest + str_ext
      if os.path.isfile(dest):
         raise ExistingBackupException()
      try:
         sh.copyfile(path,dest)
      except Exception as e:
         raise PermissionDeniedException()
      return dest

   def get_folder_size(self, path):
      total_size = 0
      for dirpath, dirnames, filenames in os.walk(path):
         for f in filenames:
               fp = os.path.join(dirpath, f)
               # skip if it is symbolic link
               if not os.path.islink(fp):
                  total_size += os.path.getsize(fp)

      return total_size

   
   def retake_file_number(self, path):
      elems = 1
      for ele in os.scandir(path):
         elems+=1
      return elems
      

   def create_dict(self, folder):
      folderDict = dict()
      folderDict["folder_path"] = self.remove_file_extension(folder)
      folderDict["folder_path_obj"] = Path(folderDict["folder_path"])
      folderDict["folder_parent"] = folderDict["folder_path_obj"].parent.absolute()
      folderDict["folder_name"] = os.path.basename(folderDict["folder_path"])
      folderDict["volume_path"] = folderDict["folder_parent"].__str__()+os.sep+folderDict["folder_name"]+".bin"
      return folderDict
   
   def delete_vol(self, path):
      path_obj = Path(path)
      os.chdir(path_obj.parent.absolute())
      os.remove(path)
   
   def removeFolder(self, path):
      os.rmdir(path)      
   
   def remove_file_extension(self, name):
      return os.path.splitext(name)[0]
   
   def restore_files(self, path, name):
      name_noExt = self.remove_file_extension(name)
      os.mkdir(name_noExt)
      self.move_files("X:", path)
            

   def fetch_size(self, path):
      aux_size = self.get_folder_size(path) 
      size = math.ceil(((1.75 * aux_size)/1024)/1024)
      threshold = 20
      size_exported = max(size, threshold)
      self.cmd_volumesize = repr(size_exported)+"M"
      return self.cmd_volumesize



   def move_files(self, source_folder, destination_folder):
      os.chdir(source_folder)
      contents = os.listdir(source_folder)
  
      for f in contents:
         if f != "System Volume Information":
               sh.move(source_folder.__str__() + os.sep + f, destination_folder.__str__() + os.sep +  f)


   
   def folder_aggregation(self,path,volname,file_number):
         os.chdir(path)
         name = path.__str__()+os.sep+volname
         os.mkdir(volname)
         for i in range(1,file_number):
            chunk_file_name = volname+"_"+repr(i)+".bin.enc"
            if os.path.isfile(chunk_file_name):
               sh.move(os.path.abspath(chunk_file_name), name)  
         return 0

      

   def folder_decomposition(self,path,volname,file_number):
      try:
         name = path.__str__()+os.sep+volname
         os.chdir(name)
         for i in range(1,file_number):
               chunk_file_name = volname+"_"+repr(i)+".bin.enc"
               if os.path.isfile(chunk_file_name):
                  sh.move(chunk_file_name,path)  
         os.chdir(path)
         os.rmdir(volname)
         return 0
      except Exception as e:
         return -1


