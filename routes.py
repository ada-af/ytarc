from werkzeug.utils import redirect
from models import LinkObject
from os import link, remove
from flask import render_template
from flask.globals import request
from flask.helpers import send_file
from config import App, db
import updater

@App.context_processor
def utility_processor():
    return dict(update_status=updater.update_status)

@App.route("/favicon.ico")
def favicon():
    return send_file("static/images/favicon.ico")

@App.route("/")
def index():
    return render_template('index.html')

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
        lo.check_updates = True if request.form['chkupdates'] == 'on' else False
        lo.driver = request.form['driver']
        lo.linktype = request.form['linktype']
        lo.driver_options = [x.strip() for x in request.form['driveroptions'].split(',')]
        db.session.merge(lo)
        db.session.commit()
        return redirect("/subscriptions")

@App.route('/editor/new', methods=['GET', 'POST'])
def editor_edit():
    if request.method == "GET":
        return render_template('editor.html')
    else:
        if request.form['url'] == '':
            return redirect("/editor/new")
        lo = LinkObject()
        lo.link = request.form['url']
        lo.check_updates = True if request.form['chkupdates'] == 'on' else False
        lo.driver = request.form['driver']
        lo.linktype = request.form['linktype']
        lo.driver_options = [x.strip() for x in request.form['driveroptions'].split(',')]
        try:
            db.session.add(lo)
            db.session.commit()
        except:
            db.session.rollback()
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
            lo.check_updates = True if request.form['chkupdates'] == 'on' else False
            lo.driver = request.form['driver']
            lo.linktype = request.form['linktype']
            lo.driver_options = [x.strip() for x in request.form['driveroptions'].split(',')]
            try:
                db.session.add(lo)
                db.session.commit()
            except:
                db.session.rollback()
        return redirect("/subscriptions")

@App.route('/upload')
def upload():
    return render_template("upload.html")