from flask import current_app, request, abort
from functools import wraps
from model import User
import hashlib
import jwt
import os

def authentication(f):
  @wraps(f)
  def decorator(*args, **kwargs):
    try:
      token = token = request.headers['Authorization']
      data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
      current_user = User.query.filter_by(uid=data['carrier']['uid']).first()

    except jwt.exceptions.ExpiredSignature as e:
      abort(401, {'authorizationError': 'Token Expired'})

    except jwt.exceptions.DecodeError as e:
      abort(401, {'authorizationError': 'Invalid authorization'})

    except KeyError as e:
      abort(401, {'authorizationError': 'Invalid authorization header'})


    return f(current_user, *args, **kwargs)
  return decorator