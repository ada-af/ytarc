from os import remove
from flask import render_template
from flask.helpers import send_file
from config import App

@App.route("/favicon.ico")
def favicon():
    return send_file("static/images/favicon.ico")

@App.route("/")
def index():
    return render_template('index.html')

@App.route('/subscriptions')
def subscriptions_list():
    return render_template('subscriptions.html')

@App.route('/editor/new')
def editor_edit():
    return render_template('editor.html')

@App.route('/editor/new/bulk')
def editor_edit_bulk():
    return render_template('editor.html', bulk=True)