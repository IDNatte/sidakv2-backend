"""Authorization & Authenticaton Decorator and Function"""


from flask import current_app, request, abort
from app.helper import token_parser
from mongoengine import errors
from functools import wraps
from app.model import User
import requests as r
import jwt


ALLOWED_EXTENSIONS = {'pdf'}
ALLOWED_EXTENSIONS_IMG = {'jpg', 'png'}


def authentication(f):
    """Authentication Decorator"""
    @wraps(f)
    def decorator(*args, **kwargs):
        try:
            auth_payload = request.headers['Authorization']
            token = token_parser.parse(auth_payload)
            if token:
                data = jwt.decode(
                    token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
                current_user = User.objects.get(id=data['carrier']['uid'])
                if current_user.is_active == True:
                    return f(current_user, *args, **kwargs)

                else:
                    abort(401, {'authorizationError': 'Account terminated !'})
            else:
                abort(401, {'authorizationError': 'Missing bearer token'})

        except jwt.exceptions.ExpiredSignatureError:
            abort(401, {'authorizationError': 'Token Expired'})

        except jwt.exceptions.DecodeError:
            abort(401, {'authorizationError': 'Invalid authorization key'})

        except KeyError as e:
            abort(401, {'authorizationError': 'Missing authorization header'})

        except errors.DoesNotExist as e:
            print(e)
            abort(401, {'authorizationError': 'account not registered'})

    return decorator


def allowed_file(filename):
    """Allowed file extension filter function"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def allowed_file_img(filename):
    """Allowed image extension filter function"""

    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_IMG
