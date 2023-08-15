import datetime
import os
import time
import urllib.request
from datetime import datetime
from distutils.log import debug
from operator import imod
from os import path
import openai

import pytz
from flask import (Blueprint, Flask, Response, flash, redirect,
                   render_template, request, send_from_directory, session,
                   url_for)
from flask_login import LoginManager, current_user, login_manager
from flask_socketio import SocketIO, emit, join_room, leave_room, send
from flask_sqlalchemy import SQLAlchemy
# from flask_debugtoolbar import DebugToolbarExtension
from werkzeug.utils import secure_filename

socketio = SocketIO()
#socketio = SocketIO(engineio_logger=True, ping_timeout=5, ping_interval=5)

db = SQLAlchemy()
DB_NAME = 'database.db'

def create_app():
    app = Flask(__name__)
    app.debug = debug
    SQLALCHEMY_POOL_RECYCLE = 35  # value less than backend’s timeout
    SQLALCHEMY_PRE_PING = True
    app.config['SECRET_KEY'] = 'IloveLilly'
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1000 * 1000
    app.config['SOCK_SERVER_OPTIONS'] = {'ping_interval': 25}
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': SQLALCHEMY_POOL_RECYCLE, 'pool_pre_ping': SQLALCHEMY_PRE_PING}
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://later:flower7@192.168.0.87:33060/nerd'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///' + DB_NAME
    db.init_app(app)

    from .views import views

    app.register_blueprint(views, url_prefix='/')

    db.create_all(app=app)

    socketio.init_app(app, cors_allowed_origins="*")
    return app


