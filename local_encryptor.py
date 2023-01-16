import os
from encryptor import Encryptor
from asyncio.windows_events import NULL
import shutil
import time
from encryption_module import Encryption_utils

class Local_encryptor(Encryptor):
    def __init__(self,ctr):
        super().__init__(ctr)
    

    def encrypt(self,folder,password,enc,hash,fs):
        try:
            self.utils = Encryption_utils(folder,0)
        except Exception as e:
            raise e
        self.utils.encryption_params(self.utils.folderDict,enc,hash,fs)
        self.utils.password_input(password)
        t_start = time.time()
        try:
            self.utils.deep_layer_encryption()
            self.utils.milestone_encryption(self.ctr.SSEpath)
            self.utils.outer_layer_encryption()
        except Exception as e:
            shutil.rmtree(self.utils.backup)
            raise e
        if os.path.isdir(self.utils.backup):
            shutil.rmtree(self.utils.backup)
        t_end = time.time()
        elapsed = t_end-t_start
        return self.utils.folderDict


    def decrypt(self,folder, password):
        self.utils = Encryption_utils(folder, 1)
        self.utils.password_input(password)
        try:
            self.utils.decryption_init()
        except Exception as e:
            raise e
        t_start = time.time()
        try:
            self.utils.outer_layer_decryption()
            self.utils.milestone_decryption()
            self.utils.deep_layer_decryption()
        except Exception as e:
            raise e
        t_end = time.time()
        elapsed = t_end-t_start
        return self.utils.folderDict


    
        
