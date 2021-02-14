from abc import ABC, abstractmethod

class BaseDriver(ABC):

    def __init__(self):
        self.filename = None
        self.title = None
        self.original_filename = None
        self.filedata = None

    @abstractmethod
    def load(self):
        ...

    @abstractmethod
    def getsha256sum():
        ...

    def cleanup(self):
        pass