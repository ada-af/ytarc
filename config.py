from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import sys

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
App = Flask(__name__)


App.config["THREADS_PER_PAGE"] = 2
App.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///storage.db" 
App.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(App)