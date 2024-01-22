import os

from flask import Flask
from flask import psql
from flask import LoginManager
from flask  import Bcrypt
from . import views, models

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config.from_object('app.config.Config')

db = psql(app)
bc = Bcrypt(app) 
lm = LoginManager() 
lm.init_app(app)       


@app.request
def initialize_database():
    db.create_all()

