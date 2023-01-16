import os
import pathlib
import math
import shutil
import subprocess
import hashlib
import dataSekura_exceptions
from file_system import File_System_Dealer as fsd

class File_alterator:
    def __init__(self, ctr):
        self.ctr = ctr
        self.pwdperm = self.ctr.pw
        self.pwdDict = dict()
        self.ssepath = self.ctr.SSEpath
        return
    
    def populateDict(self, alpha, beta, length,base):
        basePos = (alpha + (length*beta)) % length

        self.pwdDict[1] = self.pwdperm.password_permutation(base)
        self.pwdDict[2] = self.pwdperm.password_permutation(base[::-1])
        for i in range(3, self.file_number):
            index = ((basePos^i)+alpha)%length
            aux1 = self.pwdDict[i-1]
            aux2 = self.pwdDict[i-2]
            init_aux1 = aux1[0:index]
            end_aux1 =  aux1[index:(length-1)]
            aux1 = (self.pwdperm.pwd_part_A(init_aux1)) + end_aux1

            index = ((index^i)+alpha)%length
            init_aux2 = aux2[0:index]
            end_aux2 =  aux2[index:(length-1)]
            aux2 = init_aux2 + self.pwdperm.pwd_part_B(end_aux2)
            comb = self.pwdperm.merge(aux1,aux2)
            comb = comb[::-1]
            self.pwdDict[i] = comb
    
    
    
    def intermediate_encryption(self,ssepath):
        if self.ssepath == "":
            self.ssepath = ssepath
        for i in range(1,self.file_number):
            chunk_file_name = self.parentPath.__str__() + os.sep+ self.base_file_name+"_"+repr(i)+".bin"
            if os.path.isfile(chunk_file_name+".enc"):
                os.remove(chunk_file_name+".enc") #This can only happen because of a failed encryption
            if os.path.isfile(chunk_file_name):
                os.chdir(self.ssepath)
                subprocess.call(['java', '-Xmx1g', '-jar', 'ssefenc.jar', chunk_file_name, self.pwdDict[i], 'aes'])
                os.chdir(self.parentPath)
                os.remove(chunk_file_name)
            else:
                raise dataSekura_exceptions.MilestoneException()
        return 0

    def intermediate_decryption(self, parentPath, basename):
        self.parentPath = parentPath
        self.base_file_name = basename
        for i in range(1,self.file_number):
            decrypted_name = self.parentPath.__str__() + os.sep+ self.base_file_name+"_"+repr(i)+".bin"
            if os.path.isfile(decrypted_name):
                os.remove(decrypted_name)
            chunk_file_name = self.parentPath.__str__() + os.sep+ self.base_file_name+"_"+repr(i)+".bin.enc"
            if(os.path.isfile(chunk_file_name)):
                os.chdir(self.ssepath)
                subprocess.call(['java', '-Xmx1g', '-jar', 'ssefenc.jar', chunk_file_name, self.pwdDict[i], 'aes'])
                os.chdir(self.parentPath)
                if os.path.isfile(decrypted_name):
                    os.remove(chunk_file_name)
                else:
                    for i in range(1,self.file_number):
                        chunk_file_name = self.parentPath.__str__() + os.sep+ self.base_file_name+"_"+repr(i)+".bin.enc"
                        if(os.path.isfile(chunk_file_name)):
                            os.remove(chunk_file_name)
                    raise dataSekura_exceptions.IncorrectPasswordException()
            else:
                raise dataSekura_exceptions.MilestoneDecryptionException()
        return 0
    
    def intermediate_masking(self, parentPath, basename):
        self.parentPath = parentPath
        self.base_file_name = basename
        file_list = []
        try:
            for i in range(1,self.file_number):
                chunk_file_name = self.parentPath.__str__() + os.sep+ self.base_file_name+"_"+repr(i)+".bin.enc"
                if(os.path.isfile(chunk_file_name)):
                    passBytes = bytes(chunk_file_name,"ascii") 
                    name = hashlib.sha512(passBytes).hexdigest()
                    os.rename(chunk_file_name,name)
                    file_list.append(name)
                else:
                    return -1
            return file_list
        except Exception as e:
            raise e

    def split_file(self, path, volName):
        pathObj = pathlib.Path(path)
        self.parentPath = pathObj.parent.absolute()
        os.chdir(self.parentPath)
        CHUNK_SIZE = int(math.floor(os.path.getsize(path) / (self.pwdperm.beta+4)))
        total, used, free = shutil.disk_usage(path)
        free_space_MB = free // (2**20)
        space_required = (os.path.getsize(path)/1024)/1024
        if space_required < free_space_MB:
            self.file_number = 1
            with open(path, 'rb') as f:
                chunk = f.read(CHUNK_SIZE)
                while chunk:
                    self.base_file_name = volName
                    chunk_file_name = volName+"_"+repr(self.file_number)+".bin"
                    if os.path.isfile(chunk_file_name):
                        os.remove(chunk_file_name) #Let's be honest: Who is going to have a file named like this?
                    chunk_file = open(chunk_file_name,'wb')
                    chunk_file.write(chunk)
                    self.file_number += 1
                    chunk = f.read(CHUNK_SIZE)
            f.close()
            os.remove(path)
        
    
    
    def restore_file(self,basename):
        os.chdir(self.parentPath)
        fname = basename + ".bin"
        with open(fname, "wb") as myfile:
            i = 1
            while i < self.file_number:
                chunk_file_name = basename+"_"+repr(i)+".bin"
                file = open(chunk_file_name, "rb")
                myfile.write(file.read())
                file.close()
                os.remove(chunk_file_name)
                i = i +1
        myfile.close()


    def set_file_number(self, file_number):
        self.file_number = file_number