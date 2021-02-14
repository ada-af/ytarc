import threading
from drivers import loader
from config import App, db
import os
from flask import Response, redirect
from models import LinkObject, StorageObject
import importlib
from sqlalchemy import or_
import queue
import helpers
from random import shuffle

q = queue.SimpleQueue()

def background_update_task():
    for lo in LinkObject.query.filter_by(driver='ytdl', check_updates=True).all():
        helpers.get_metadata(lo.link, lo.driver_options, lo.id, lo.linktype)
    loadable_objects = StorageObject.query.filter(or_(StorageObject.filename==None, StorageObject.filename=='')).all()
    shuffle(loadable_objects)
    for so in loadable_objects:
        q.put(so)
    while not q.empty():
        so = q.get(False)
        print(f"Loading {so.url}")
        dri = importlib.import_module(f'drivers.{so.get_owner().driver}')
        l = loader.DownloaderThread(dri.Driver, so)
        l.run()
    os.remove('update.lck')

@App.route("/update")
def update():
    if os.path.exists('update.lck'):
        return redirect('/')
    else:
        open('update.lck', 'w')
        t = threading.Thread(target=background_update_task, daemon=True)
        t.start()
        return redirect('/')

@App.route("/update/status")
def update_status():
    if not os.path.exists('update.lck'):
        return False
    else:
        t = len(StorageObject.query.all())
        return str((t-q.qsize())/t * 100)