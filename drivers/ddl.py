from models import StorageObject
from drivers.BaseDriver import BaseDriver
import requests
from hashlib import sha256
import re

class Driver(BaseDriver):

    def __init__(self, obj: StorageObject):
        BaseDriver.__init__(self)
        self.obj = obj

    def load(self):
        r = requests.get(self.obj.url, allow_redirects=True)
        if r.headers.get('Content-Type') == 'text/html':
            g = re.search("<title>(.*)</title>", r.content)
            self.title = g.group(1)
        self.original_filename = r.url.split('/')[-1].split('?')[0]
        self.filedata = r.content
    
    def getsha256sum(self):
        return sha256(self.filedata).hexdigest()