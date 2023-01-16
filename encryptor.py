class Encryptor:
    def __init__(self, ctr):
        self.ctr = ctr
        self.fs = self.ctr.fs
        self.pw = self.ctr.pw
        self.ux = self.ctr.ux
        self.VCpath = self.ctr.VCpath
        self.SSEpath = self.ctr.SSEpath
        self.vc = self.ctr.vc
        self.fd = self.ctr.fd  
        
    def encrypt(folder):
        pass
    def decrypt(folder):
        pass