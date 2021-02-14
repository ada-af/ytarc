from time import sleep
from config import db
from models import StorageObject, Tag
from youtube_dl import YoutubeDL
import time
from random import randint

def insert_nofail(obj):
    try:
        db.session.add(obj)
        db.session.commit()
    except:
        db.session.rollback()
        db.session.merge(obj)
        db.session.commit()
    return obj


def ddl_get_metadata(url, owner, filetype):
    so = StorageObject()
    so.origin = 'remote'
    so.url = url
    so.owned_by = owner
    so.filetype = filetype
    so = insert_nofail(so)
    to = Tag()
    to.tagged_object = so.id
    to.name = f"type:{filetype.lower()}"
    insert_nofail(to)
    
    

def get_metadata(url, options, owner, filetype):

    def filler(object):
        so = StorageObject()
        so.description = object['description']
        so.title = object['title']
        so.origin = 'remote'
        so.url = object['webpage_url']
        so.owned_by = owner
        so.filetype = filetype
        so = insert_nofail(so)
        to = Tag()
        to.tagged_object = so.id
        to.name = f"type:{filetype.lower()}"
        insert_nofail(to)
        
    ydl = YoutubeDL()
    md = ydl.extract_info(url, download=False)
    if 'entries' in md.keys():
        for i in md['entries']:
            filler(i)
    else:
        filler(md)
    return