from asyncio.windows_events import NULL
import subprocess
import sys
from file_system import File_System_Dealer
from local_encryptor import Local_encryptor
from password_permutator import Password_permutator
from veracrypt import Veracrypt
from file_dealing import File_alterator
import os

class Controller:
    def __init__(self,gui):
        self.gui = gui
        self.dataSekura_setUp()
    
    def dataSekura_setUp(self):
        self.fs = File_System_Dealer()
        self.pw = Password_permutator()
        self.base = os.getcwd()
        self.VCpath = self.fs.check_VC_integrity()
        self.SSEpath = self.fs.check_SSFEnc_integrity()
        return 0


    def encryption(self,folder,password,enc,hash,fs):
        self.encryptor = Local_encryptor(self)
        try:
            self.encryptor.encrypt(folder,password,enc,hash,fs)
        except Exception as e:
            return -1
    
    def decryption(self,folder,pwd):
        self.encryptor = Local_encryptor(self)
        try:
            self.encryptor.decrypt(folder,pwd)
        except Exception as e:
            return -1


