from operator import sub
from traceback import print_tb
from youtube_dl import YoutubeDL
from youtube_dl import options
from .BaseDriver import BaseDriver
from models import StorageObject
import shutil
import pathlib
import os
from random import randint
from hashlib import sha256
import subprocess

class Driver(BaseDriver):

    def __init__(self, obj: StorageObject):
        BaseDriver.__init__(self)
        self.obj = obj
        self.options = self.obj.get_owner().driver_options
        self.options.update({'outtmpl': f'basefilename.{randint(1000, 9000)}'})

    def load(self):
        ytdl = YoutubeDL(self.options)
        ytdl.download([self.obj.url])
        tmp = ytdl.extract_info(self.obj.url, download=False)
        self.tmp_fname = [x for x in os.listdir() if x.startswith(self.options['outtmpl'])][0]
        if self.tmp_fname.endswith('mkv'):
            self._tomp4()
        else:
            shutil.move(self.tmp_fname, "storage/"+self.tmp_fname)
            self._calcsha256()
        self.original_filename = tmp['title']+"."+self.tmp_fname.split('.')[-1]
    
    def _tomp4(self):
        subprocess.run(['ffmpeg', '-i', self.tmp_fname, '-acodec', 'copy', '-vcodec', 'copy', '-y', "storage/"+self.tmp_fname+".mp4"])
        os.remove(self.tmp_fname)
        self.tmp_fname = self.tmp_fname+".mp4"
        self._calcsha256()


    def _calcsha256(self):
        hashfunc = sha256()
        with open("storage/"+self.tmp_fname, 'rb') as f:
            x = f.read(65535)
            while len() > 0:
                hashfunc.update(x)
                x = f.read(65535)
        self.sha256sum = hashfunc.hexdigest()
    
    def getsha256sum(self):
        return self.sha256sum

    def cleanup(self):
        filename = f"{self.sha256sum[:16]}.{self.tmp_fname.split('.')[-1]}"
        pathlib.Path(f"storage/{self.sha256sum[:2]}").mkdir(parents=True, exist_ok=True)
        shutil.move(f"storage/{self.tmp_fname}", f"storage/{self.sha256sum[:2]}/{filename}")