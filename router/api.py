from flask import Blueprint, jsonify, request, g, redirect, url_for, abort, current_app
# from helper import authentication
from functools import wraps
from model import User
from config import db
import sqlalchemy
import platform
import datetime
import flask
import time
import jwt
import os

api_endpoint = Blueprint('api_endpoint', __name__)

def authentication(f):
  @wraps(f)
  def decorator(*args, **kwargs):
    try:
      token = token = request.headers['Authorization']
      data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
      current_user = User.query.filter_by(email=data['carrier']['email'], username=data['carrier']['username']).first()
    except jwt.exceptions.ExpiredSignature as e:
      abort(401, {'authorizationError': 'token Expired'})

    except KeyError as e:
      abort(401, {'authorizationError': 'Invalid authorization header'})

    return f(current_user, *args, **kwargs)
  return decorator

@api_endpoint.before_app_request
def before_request():
  g.request_start_time = time.time()
  g.request_time = lambda: "%.5fs" %(time.time() - g.request_start_time)

@api_endpoint.app_errorhandler(401)
@api_endpoint.app_errorhandler(405)
@api_endpoint.app_errorhandler(404)
def errorhandler(error):
  return jsonify({"status": error.code, "message": error.description})

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

@api_endpoint.route('/api/auth/login', methods=["POST"])
def authorization():
  if request.method == "POST":
    try:
      email = request.get_json()['email']
      password = request.get_json()['password']
      
      user_data = User.query.filter_by(email=email).one()
      passwd_authentication = user_data.check_password(request.get_json()['password'])

      if passwd_authentication:
        token_exp = datetime.datetime.utcnow() + datetime.timedelta(weeks=2)
        token = jwt.encode({
          "carrier": {
            "email": user_data.email,
            "username": user_data.username
          },
          'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=1), 
        }, current_app.config['SECRET_KEY'], algorithm='HS256')

        return jsonify({"access_token": token.decode('UTF-8'), "expired": token_exp})

    except KeyError as e:
      abort(401, {'authorizationError': 'Not sufficient or wrong argument given'})

    except sqlalchemy.exc.NoResultFound as e:
      abort(401, {'authorizationError': 'User unavailable'})


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
    abort(405, {'InvalidRequestBodyError': 'Not sufficient or wrong argument given'})

@api_endpoint.route('/user/me', methods=["GET"])
@authentication
def get_me(current_user):
  # print(current_user.u)
  return jsonify({
    "username" : current_user.username,
    "email": current_user.username,
    "password": "*****"
  })

@api_endpoint.route('/api/resource', methods=["GET"])
@authentication
def resource():
  return jsonify({'secret': 'himichuu'})