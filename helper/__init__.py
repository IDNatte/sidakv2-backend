"""Helper class"""
from flask import current_app, request, abort
from functools import wraps
from model import User
import jwt

def authentication(f):
  """Authentication helper"""
  @wraps(f)
  def decorator(*args, **kwargs):
    try:
      token = token = request.headers['Authorization']
      data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
      current_user = User.objects.get(id=data['carrier']['uid'])
      return f(current_user, *args, **kwargs)

    except jwt.exceptions.ExpiredSignature:
      abort(401, {'authorizationError': 'Token Expired'})

    except jwt.exceptions.DecodeError:
      abort(401, {'authorizationError': 'Invalid authorization key'})

    except KeyError:
      abort(401, {'authorizationError': 'Invalid authorization header'})

  return decorator