import threading
from models import StorageObject
from config import App

status = 60

@App.route("/update")
def update():
    pass

@App.route("/update/status")
def update_status():
    if status == 0 or len(StorageObject.query.all()) == 0:
        return False
    else:
        return status/len(StorageObject.query.all()) * 100