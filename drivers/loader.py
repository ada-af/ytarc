import time
from flask.wrappers import Response
from werkzeug.utils import redirect
from drivers.BaseDriver import BaseDriver
from models import StorageObject
from config import db
import pathlib
import subprocess

class DownloaderThread():

    def __init__(self, driver, obj):
        self.obj: StorageObject = obj
        self.driver = driver(obj)

    def flush(self):
        if self.driver.filedata is not None:
            pathlib.Path(f'storage/{self.obj.filename[:2]}').mkdir(parents=True, exist_ok=True)
            with open(f"storage/{self.obj.filename[:2]}/{self.obj.filename}", 'wb') as f:
                f.write(self.driver.filedata)
        

    def gen_preview(self):
        pathlib.Path(f'storage/preview/{self.obj.filename[:2]}').mkdir(parents=True, exist_ok=True)
        self.obj.preview = True
        if self.obj.filetype == 'photo':
            subprocess.run(['ffmpeg', '-i', f"storage/{self.obj.filename[:2]}/{self.obj.filename}", "-vf", "scale=360:-1", "-y", f"storage/preview/{self.obj.filename[:2]}/{self.obj.filename}.webp"])
        else:
            subprocess.run(['ffmpeg', '-i', f"storage/{self.obj.filename[:2]}/{self.obj.filename}", "-vf", "scale=360:-1", "-loop", "9", "-r", "1", "-y", f"storage/preview/{self.obj.filename[:2]}/{self.obj.filename}.webp"])

    def flush_db(self):
        db.session.merge(self.obj)
        while True:
            try:
                db.session.commit()
                break
            except:
                print("Something locks db wating")
                time.sleep(0.2)

    def run(self):
        self.driver.load()

        if self.driver.title:
            self.obj.title = self.driver.title
        self.obj.sha256sum = self.driver.getsha256sum()
        self.obj.original_filename = self.driver.original_filename
        self.obj.filename = f"{self.obj.sha256sum[:16]}.{self.obj.original_filename.split('.')[-1]}"

        self.driver.cleanup()

        self.flush()
        
        if self.obj.filetype in ['video', 'photo']:
            self.gen_preview()

        self.flush_db()

        return