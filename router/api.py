from flask import Blueprint, jsonify, request, g, redirect, url_for, abort, current_app
from model import User, UserFileEntry, dbhelper
from helper import authentication
from config import db
import sqlalchemy
import platform
import datetime
import flask
import json
import time
import jwt
import os

api_endpoint = Blueprint('api_endpoint', __name__)

@api_endpoint.before_app_request
def before_request():
  g.request_start_time = time.time()
  g.request_time = lambda: "%.5fs" %(time.time() - g.request_start_time)


# error handler API
@api_endpoint.app_errorhandler(400)
@api_endpoint.app_errorhandler(401)
@api_endpoint.app_errorhandler(405)
@api_endpoint.app_errorhandler(404)
def errorhandler(error):
  return jsonify({"status": error.code, "message": error.description})

# server info API
@api_endpoint.route('/api', methods=['GET'])
def server_info():
  sv_info = {
    "flask_ver": flask.__version__,
    "python_ver": platform.sys.version,
    "build_status": os.environ['FLASK_ENV'],
    "operating_system": platform.system(),
    "current_timestamp": datetime.datetime.now(),
    "load_time": g.request_time()
  }

  return jsonify(sv_info)

# authorization API
@api_endpoint.route('/api/auth/login', methods=["POST"])
def authorization():
  if request.method == "POST":
    try:
      email = request.get_json()['email']
      password = request.get_json()['password']
      
      user_data = User.query.filter_by(email=email).one()
      passwd_authentication = user_data.check_password(request.get_json()['password'])

      if passwd_authentication:
        token_exp = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        token = jwt.encode({
          "carrier": {
            "uid": user_data.uid
          },
          'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1), 
        }, current_app.config['SECRET_KEY'], algorithm='HS256')

        return jsonify({"access_token": token.decode('UTF-8'), "expired": token_exp})

    except KeyError as e:
      abort(401, {'authorizationError': 'Not sufficient or wrong argument given'})

    except sqlalchemy.exc.NoResultFound as e:
      abort(401, {'authorizationError': 'User unavailable'})

@api_endpoint.route('/api/auth/register', methods=["POST"])
def register():

  try:
    file_directory = './data/json/{0}-{1}.json'.format(dbhelper.UUIDGenerator(), request.get_json()['org'])
    username = request.get_json()['username']
    password = request.get_json()['password']
    email = request.get_json()['email']
    org = request.get_json()['org']

    u = User(email=email, username=username, org=org)
    u.content = [UserFileEntry(fileURL=file_directory)]
    u.set_password(password)
    db.session.add(u)
    db.session.commit()

    db_selector = User.query.filter_by(email=email).first()

    send_back = {
      "user_id": db_selector.uid,
      "username": db_selector.username,
      "email": db_selector.email,
      "password": "protected",
      "org": db_selector.org,
      "status": "registered"
    }

    return jsonify(send_back)

  except sqlalchemy.exc.IntegrityError as e:
    abort(401, {'UserExistError': 'Account already registered'})

  except KeyError as e:
    abort(401, {'InvalidRequestBodyError': 'Not sufficient or wrong argument given'})

# user info API
@api_endpoint.route('/api/user/me', methods=["GET"])
@authentication
def get_me(current_user):
  return jsonify({
    "username" : current_user.username,
    "email": current_user.email,
    "password": "*****",
    "org": current_user.org
  })

# resource API
@api_endpoint.route('/api/resource', methods=["GET", "POST"])
@authentication
def resource(current_user):
  if request.method == 'GET':
    dyn_fileentry = db.session.query(UserFileEntry).join(User).filter(User.uid==current_user.uid).first()
    try:
      with open(dyn_fileentry.fileURL, 'r') as data_content:
        return jsonify(json.loads(data_content.read()))
    except FileNotFoundError:
      abort(404, {'EmptyDataEntry': 'your data entry is still empty'})

  elif request.method == 'POST':
    if request.headers.get('Content-Type') == 'application/json':
      dyn_fileentry = db.session.query(UserFileEntry).join(User).filter(User.uid==current_user.uid).first()
      with open(dyn_fileentry.fileURL, 'w') as wdhard:
        json.dump(request.get_json(), wdhard)

    else:
      abort(400, {'TypeError': 'You submitted non-json body!'})


  return jsonify({'secret': 'c'})