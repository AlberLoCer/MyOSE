from asyncio.windows_events import NULL
import os
import hashlib
from file_system import File_System_Dealer
from password_permutator import Password_permutator
from veracrypt import Veracrypt
from file_dealing import File_alterator

class Encryption_utils:
    def __init__(self, folder, op):
        self.fs = File_System_Dealer()
        self.pw = Password_permutator()
        self.ux = User_choices()
        self.VCpath = self.fs.check_VC_integrity()
        self.SSEpath = self.fs.check_SSFEnc_integrity()
        self.vc = Veracrypt(self.VCpath)
        self.fd = File_alterator(self)      
        if op == 0:
            init = self.init_Enc(folder)
            if init == -1:
                raise dataSekura_exceptions.PermissionDeniedException()
            elif init == 0:
                raise dataSekura_exceptions.ExistingBackupException()
        elif op == 1:
            self.init_Dec(folder)
        else:
            self.folderDict = NULL
        return
    
    def init_Enc(self,folder):
        self.folderDict = self.fs.create_dict(folder)       
        try:
            self.checkPermissions(self.folderDict['folder_path'])
        except Exception as e:
            return -1
        self.backup = self.fs.directory_backup_create(self.folderDict['folder_path'])
        if self.backup == 0:
            return 0

    def init_Dec(self,folder):
        self.folderDict = self.fs.create_dict(folder)
    
    def checkPermissions(self,source_folder):
        os.chdir(source_folder)
        for root, subdirectories, files in os.walk(source_folder):
            for file in files:
                path = os.path.join(root, file)
                os.chmod(path,0o777)
                if os.access(path, os.X_OK | os.W_OK | os.R_OK) == False:
                    raise Exception

            for subdirectory in subdirectories:
                path = os.path.join(root, subdirectory)
                os.chmod(path,0o777)
                if os.access(path, os.X_OK | os.W_OK | os.R_OK) == False:
                    raise Exception
            
        return 0
    
    def deep_layer_encryption(self):
        if os.path.isfile(self.folderDict["volume_path"]):
            raise dataSekura_exceptions.VolumeException()
        elif os.path.isdir("X:"+os.sep):
            raise dataSekura_exceptions.DriveXexception()
            
        try: self.vc.VC_Encryption(self.folderDict["volume_path"], self.permuted_password, self.cmd_hash, self.cmd_encryption, self.cmd_fs, self.volume_size, self.folderDict["folder_path"])
        except Exception as e:
            raise e


    def milestone_encryption(self,ssepath):
        if self.SSEpath == "":
            self.SSEpath = ssepath
        if self.fd.split_file(self.folderDict["volume_path"], self.folderDict["folder_name"]) != -1:
            self.fd.populateDict(self.pw.get_alpha(),self.pw.get_beta(),len(self.permuted_password),self.permuted_password)
            try: self.fd.intermediate_encryption(ssepath)
            except Exception as e:
                raise e
        else:
            raise dataSekura_exceptions.SplitFileException()
        return
            
        
    
    def outer_layer_encryption(self):
        #In principle P should be 'none' if the rest was ok
        self.fs.folder_aggregation(self.folderDict["folder_parent"], self.folderDict["folder_name"], self.fd.file_number)
        self.final_pass = self.pw.password_permutation(self.permuted_password)
        self.volume_size = self.fs.fetch_size(self.folderDict["folder_path"])
        self.vc.VC_Encryption(self.folderDict["volume_path"], self.final_pass, self.cmd_hash, self.cmd_encryption, self.cmd_fs, self.volume_size, self.folderDict["folder_path"])
    
    
    def decryption_init(self):
        try:
            self.final_pass = self.pw.password_permutation(self.permuted_password)
            os.chdir(self.folderDict["folder_parent"])
            base_vol = os.path.basename(self.folderDict["volume_path"])
            self.vol_path = self.folderDict["folder_parent"].__str__() + os.sep + base_vol
            self.backup = self.fs.file_backup_creation(self.vol_path)
        except Exception as e:
            raise e
    

    def outer_layer_decryption(self):
        try:
            self.vc.VC_Decryption(self.vol_path,self.final_pass, self.folderDict["folder_path"]) == -1
        except Exception as e:
            os.remove(self.backup)
            raise e
    
    def milestone_decryption(self):
        self.fd.file_number = self.fs.retake_file_number(self.fs.remove_file_extension(self.vol_path))
        self.fd.populateDict(self.alpha_base,self.beta_base, len(self.permuted_password),self.permuted_password)
        self.fs.folder_decomposition(self.folderDict["folder_parent"], self.folderDict["folder_name"], self.fd.file_number)
        self.fd.intermediate_decryption(self.folderDict["folder_parent"], self.folderDict["folder_name"])
        self.fd.restore_file(self.folderDict["folder_name"])
    
    def deep_layer_decryption(self):
        self.vc.VC_Decryption(self.vol_path,self.permuted_password, self.folderDict["folder_path"])
        os.remove(self.backup)
    
    def password_input(self,pwd):
        self.base_password = pwd
        self.permuted_password = self.pw.password_permutation(self.base_password)
        self.alpha_base = self.pw.get_alpha()
        self.beta_base = self.pw.get_beta()


    def encryption_params(self, folderDict,encryption,hash,fs):
        self.cmd_encryption = self.ux.choose_encryption(encryption)
        self.cmd_hash = self.ux.choose_hash(hash)
        self.cmd_fs = self.ux.choose_fs(fs)
        self.volume_size = self.fs.fetch_size(folderDict["folder_path"])
   