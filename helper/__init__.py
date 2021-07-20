"""Helper class"""
from flask import current_app, request, abort
from mongoengine import errors
from functools import wraps
from model import User
import requests as r
import jwt

ALLOWED_EXTENSIONS = {'pdf'}
ALLOWED_EXTENSIONS_IMG = {'jpg', 'png'}

def recaptchaVerif(response):
  gre_key = current_app.config.get('RECAPTCHA_SECRET')
  data = {"response": response, "secret": gre_key}
  captcha_validate = 'https://www.google.com/recaptcha/api/siteverify'
  verifyCaptcha = r.post(captcha_validate, data)

  return verifyCaptcha.text

def authentication(f):
  """Authentication helper"""
  @wraps(f)
  def decorator(*args, **kwargs):
    try:
      token = token = request.headers['Authorization']
      data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
      current_user = User.objects.get(id=data['carrier']['uid'])
      if current_user.is_active == True:
        return f(current_user, *args, **kwargs)

      else:
        abort(401, {'authorizationError': 'Account terminated !'})

    except jwt.exceptions.ExpiredSignature:
      abort(401, {'authorizationError': 'Token Expired'})

    except jwt.exceptions.DecodeError:
      abort(401, {'authorizationError': 'Invalid authorization key'})

    except KeyError as e:
      print(e)
      abort(401, {'authorizationError': 'Invalid authorization header'})

    except errors.DoesNotExist as e:
      abort(401, {'authorizationError': 'account not registered'})

  return decorator

def allowed_file(filename):
  return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_file_img(filename):
  return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_IMG
