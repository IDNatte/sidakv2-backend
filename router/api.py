from flask import Blueprint, jsonify, request, g, redirect, url_for, abort
from datetime import datetime
from model import User
from config import db
import platform
import flask
import time
import os

api_endpoint = Blueprint('api_endpoint', __name__)

@api_endpoint.before_app_request
def before_request():
  g.request_start_time = time.time()
  g.request_time = lambda: "%.5fs" %(time.time() - g.request_start_time)

@api_endpoint.app_errorhandler(401)
@api_endpoint.app_errorhandler(405)
@api_endpoint.app_errorhandler(404)
def errorhandler(error):
  return jsonify({"status": error.code, "message": error.name})

@api_endpoint.route('/api', methods=['GET'])
def server_info():
  sv_info = {
    "flask_ver": flask.__version__,
    "python_ver": platform.sys.version,
    "build_status": os.environ['FLASK_ENV'],
    "operating_system": platform.system(),
    "current_timestamp": datetime.now(),
    "load_time": g.request_time()
  }

  return jsonify(sv_info)

@api_endpoint.route('/api/auth/login', methods=["POST"])
def authorization():
  if request.method == "POST":
    return jsonify({"test": "test"})

@api_endpoint.route('/api/auth/register', methods=["POST"])
def register():

  try:
    username = request.get_json()['username']
    password = request.get_json()['password']
    email = request.get_json()['email']

    u = User(email=email, username=username)
    u.set_password(password)
    db.session.add(u)
    db.session.commit()

    db_selector = User.query.filter_by(email=email).first()

    send_back = {
      "user_id": db_selector.uid,
      "username": db_selector.username,
      "email": db_selector.email,
      "password": "protected"
    }

    return jsonify(send_back)

  except KeyError as e:
    abort(405)


  # if (username & password & email):
  #   return jsonify({"status": "all_fullfiled"})

  