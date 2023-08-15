import os
import os.path
from os import path
from flask import Flask, request, jsonify
from flask_cors import CORS

from flask import (Blueprint, Response, current_app, flash, jsonify, redirect,
                   render_template, request, send_from_directory, session,
                   url_for)
from flask_login import current_user, login_required, login_user, logout_user
from requests import Response
from sqlalchemy import update
from werkzeug.datastructures import FileStorage
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

views = Blueprint('views', __name__)

@views.route("/")
def base():
   return render_template ('base.html')

@views.route("/login")
def login():
   return render_template('login.html')

@views.route("/dashboard")
def dashboard():
   return render_template('dashboard.html')

@views.route("/socialboard")
def socialboard():
   return render_template('socialboard.html')


@views.route("/editprofile")
def editprofile():
   return render_template('edit-profile.html')