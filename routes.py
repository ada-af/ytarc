from flask.wrappers import Response
from flask_sqlalchemy import Pagination
from werkzeug.utils import redirect
from models import LinkObject, StorageObject, Tag
from os import link, remove
from flask import render_template, g
from flask.globals import request
from flask.helpers import send_file, send_from_directory
from config import App, db
import threading
import helpers
from sqlalchemy.dialects import sqlite
import updater

@App.context_processor
def utility_processor():
    return dict(update_status=updater.update_status)

@App.route("/favicon.ico")
def favicon():
    return send_file("static/images/favicon.ico")

@App.route("/")
def index():
    links=LinkObject.query.order_by(LinkObject.id.desc()).all()[:5]
    objects=StorageObject.query.order_by(StorageObject.id.desc()).all()[:5]
    
    return render_template('index.html',
     links=links,
     objects=objects)

@App.route('/subscriptions')
def subscriptions_list():
    los = LinkObject.query.all()
    
    return render_template('subscriptions.html', los=los)

@App.route('/editor/edit/<id>', methods=['GET', 'POST'])
def edit_linkobject(id):
    if request.method == "GET":
        return render_template('editor.html', lo=LinkObject.query.get(id))
    else:
        lo = LinkObject.query.get(id)
        lo.link = request.form['url']
        lo.driver = request.form['driver']
        lo.check_updates = True if request.form.get('checker') == 'on' else False
        lo.linktype = request.form['linktype']
        try:
            lo.driver_options = dict([x.strip().split('=', maxsplit=1) for x in request.form['driveroptions'].split(',')])
        except:
            lo.driver_options = {}
        db.session.merge(lo)
        db.session.commit()
        
        return redirect("/subscriptions")
            
@App.route("/preview/<id>.webp")
def preview(id):
    so = StorageObject.query.filter_by(id=id).first()
    
    try:
        return send_file(f"storage/preview/{so.filename[:2]}/{so.filename}.webp")
    except:
        return Response("Not found", 404)

@App.route('/editor/new', methods=['GET', 'POST'])
def editor_edit():
    if request.method == "GET":
        return render_template('editor.html')
    else:
        if request.form['url'] == '':
            return redirect("/editor/new")
        lo = LinkObject()
        lo.link = request.form['url']
        lo.check_updates = True if request.form.get('checker') == 'on' else False
        lo.driver = request.form['driver']
        lo.linktype = request.form['linktype']
        try:
            lo.driver_options = dict([x.strip().split('=', maxsplit=1) for x in request.form['driveroptions'].split(',')])
        except:
            lo.driver_options = {}
        try:
            db.session.add(lo)
            db.session.commit()
            
        except:
            db.session.rollback()
        if lo.driver == 'ytdl':
            helpers.get_metadata(lo.link, lo.driver_options, lo.id, lo.linktype)
        else:
            helpers.ddl_get_metadata(lo.link, lo.id, lo.linktype)
        
        return redirect("/subscriptions")

@App.route('/editor/new/bulk', methods=['GET', 'POST'])
def editor_edit_bulk():
    if request.method == "GET":
        return render_template('editor.html', bulk=True)
    else:
        links = set([x.strip() for x in request.form['url'].split('\n')]) - set([''])
        for i in links:
            lo = LinkObject()
            lo.link = i
            lo.driver = request.form['driver']
            lo.check_updates = True if request.form.get('checker') == 'on' else False
            lo.linktype = request.form['linktype']
            try:
                lo.driver_options = dict([x.strip().split('=', maxsplit=1) for x in request.form['driveroptions'].split(',')])
            except:
                lo.driver_options = {}
            try:
                db.session.add(lo)
                db.session.commit()
                
            except:
                db.session.rollback()
            if lo.driver == 'ytdl':
                helpers.get_metadata(lo.link, lo.driver_options, lo.id, lo.linktype)
            else:
                helpers.ddl_get_metadata(lo.link, lo.id, lo.linktype)
        
        
        return redirect("/subscriptions")

@App.route('/object/<id>')
def show_object(id):
    g.q = request.args.get('q')
    so = StorageObject.query.filter_by(id=id).first()
    
    return render_template('object.html', object=so)

@App.route('/storage/<dir>/<fname>')
def serve_content(dir, fname):
    return send_from_directory('storage', filename=f"{dir}/{fname}")

@App.route('/search')
@App.route('/search/<int:page>')
def search(page=1):
    g.q = request.args.get('q')
    if len(g.q) == 0:
        query = db.session.execute("select distinct tagged_object from tag order by tagged_object desc")
    else:
        res = [x.lower().strip() for x in request.args.get('q').split(',') if not x.lower().strip().startswith('-')]
        rem = [x.lower().strip().strip('-') for x in request.args.get('q').split(',') if x.lower().strip().startswith('-')]
        q_keys = dict()
        idx = 1
        subq = []
        rsubq = []
        for i in res:
            q_keys[f"t{idx}"] = i
            subq.append(f"SELECT tagged_object from tag where name = :t{idx}")
            idx += 1
        idx = 1
        for i in rem:
            q_keys[f"r{idx}"] = i
            rsubq.append(f"name = :r{idx}")
            idx += 1
        rq = " or ".join(rsubq)
        sq = " INTERSECT ".join(subq)
        if len(rq) > 0:
            query = db.session.execute(db.text(f'select * from ({sq}) where tagged_object not in (select tagged_object from tag where {rq}) order by tagged_object desc'), q_keys)
        else:
            query = db.session.execute(db.text(f"select * from ({sq}) order by tagged_object desc"), q_keys)
    q_res = query.fetchall()
    results = [StorageObject.query.filter_by(id=x[0]).first() for x in q_res[12*(page-1):12*(page)]]
    # print([x[0] for x in q_res])
    return render_template("search.html", results=results, page=page, pages=(len(q_res)//12))
    
