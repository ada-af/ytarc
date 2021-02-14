from re import T
from routes import preview
from models import LinkObject, StorageObject, Tag
from flask.wrappers import Response
from config import App, db
from flask import redirect, Response, request
import importlib
from drivers import loader
import helpers
import subprocess
import os

@App.route('/api/link/delete/<int:id>', methods=['DELETE'])
def delete_link(id):
    lo = LinkObject.query.get(id)
    db.session.delete(lo)
    db.session.commit()
    
    return Response("OK", 200)
    
@App.route('/api/load/<int:id>')
def load_one(id):
    so = StorageObject.query.filter_by(id=id).first()
    dri = importlib.import_module(f'drivers.{so.get_owner().driver}')
    l = loader.DownloaderThread(dri.Driver, so)
    l.run()
    return Response("OK", status=200)

@App.route('/api/link/recheck/<int:id>')
def recheck_meta(id):
    lo = LinkObject.query.get(id)
    if lo.driver == 'ddl':
        helpers.ddl_get_metadata(lo.link, lo.id, lo.linktype)
    else:
        helpers.get_metadata(lo.link, lo.driver_options, lo.id, lo.linktype)
    return Response("OK", status=200)


@App.route('/api/file/delete/<int:id>', methods=['DELETE'])
def delete_file(id):
    so = StorageObject.query.filter_by(id=id).first()
    print(so)
    os.remove(f'storage/{so.filename[:2]}/{so.filename}')
    if so.preview == True:
        os.remove(f'storage/preview/{so.filename[:2]}/{so.filename}')
    db.session.delete(so)
    db.session.commit()    
    return Response("OK", status=200)

@App.route('/api/tag/delete/<int:id>', methods=['DELETE'])
def delete_tag(id):
    to = Tag.query.get(id)
    db.session.delete(to)
    db.session.commit()    
    return Response("OK", status=200)

@App.route('/api/tag/create/<int:id>', methods=['PUT'])
def create_tag(id):
    to = Tag()
    to.tagged_object = id
    to.name = request.args.get('tag').lower().strip()
    db.session.add(to)
    db.session.commit()
    return str(to.id)

@App.route("/api/system/start/<int:id>", methods=['TOUCH'])
def start_file(id):
    so = StorageObject.query.filter_by(id=id).first()
    subprocess.call(f"{os.getcwd()}/storage/{so.filename[:2]}/{so.filename}", shell=True)
    return Response("OK", 200)