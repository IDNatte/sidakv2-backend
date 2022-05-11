"""Authorization,registration, and authentication blueprint"""


from flask import Blueprint, abort, current_app, jsonify, request
from app.helper.auth import authentication
from app.helper.csrf import paranoid_mode
from app.model import Organization, User
from app.helper import db_helper

import mongoengine
import datetime
import jwt


api_endpoint = Blueprint('authorization_api', __name__)


@api_endpoint.app_errorhandler(400)
@api_endpoint.app_errorhandler(401)
@api_endpoint.app_errorhandler(403)
@api_endpoint.app_errorhandler(405)
def errorhandler(error):
    return jsonify({"status": error.code, "message": error.description}), error.code


@api_endpoint.after_app_request
def after_request(response):
    return paranoid_mode(response)


@api_endpoint.route('/api/auth/login', methods=["POST"])
def authorization():
    if request.method == "POST":
        try:
            email = request.get_json()['email']
            password = request.get_json()['password']

            user_data = User.objects.get(email=email)
            passwd_authentication = db_helper.check_password(
                user_data.password, password)

            if user_data.is_active:
                if passwd_authentication:
                    token_exp = datetime.datetime.utcnow() + datetime.timedelta(days=1)
                    token = jwt.encode({
                        "carrier": {
                            "uid": str(user_data.id)
                        },
                        'exp': datetime.datetime.now() + datetime.timedelta(days=1),
                    }, current_app.config['SECRET_KEY'], algorithm='HS256')
                    return jsonify({"access_token": token.decode('UTF-8'), "expired": token_exp})
                else:
                    abort(401, {'authorizationError': 'Wrong password'})
            else:
                abort(401, {'authorizationError': 'Account terminated !'})

        except KeyError as e:
            abort(
                401, {'authorizationError': 'Not sufficient or wrong argument given'})

        except mongoengine.errors.DoesNotExist as e:
            abort(401, {'authorizationError': 'Email not registered'})

    else:
        abort(405, {"MethodeNotAllowed": "Forbidden methode type"})


@api_endpoint.route('/api/auth/register', methods=["GET", "POST"])
@authentication
def register(current_user):
    if request.method == 'POST':
        try:
            if current_user.lvl == 1:
                is_active = request.get_json()['is_active']
                username = request.get_json()['username']
                password = request.get_json()['password']
                email = request.get_json()['email']
                sector = request.get_json()['sector']
                org = request.get_json()['org']
                lvl = request.get_json()['lvl']

                org_search = Organization.objects.filter(
                    id=org, sector_group=sector).count()

                if org_search > 0:

                    organization = Organization.objects.filter(
                        id=org, sector_group=sector).get()
                    user = User(username=username, email=email,
                                org=organization, lvl=lvl, is_active=bool(is_active))
                    user.password = db_helper.generate_password_hash(password)
                    user.save()

                    send_back = {
                        "user_id": str(user.id),
                        "username": str(user.username),
                        "email": str(user.email),
                        "password": "protected",
                        "org": str(user.org.org_name),
                        "privilege": "admin" if int(user.lvl) == 1 else "cm_moderator",
                        "is_activated": user.is_active
                    }

                    return jsonify(send_back)

                else:
                    abort(
                        403, {'orgListError': 'No organization or sector list registered'})

            else:
                abort(
                    401, {'authorizationError': 'Only admin can perform this action !'})

        except KeyError as e:
            abort(
                403, {'InvalidRequestBodyError': 'Argument {0} not found in body'.format(e)})

        except (mongoengine.errors.NotUniqueError):
            abort(403, {'AccountError': 'Account already registered'})

        except mongoengine.errors.ValidationError:
            abort(403, {
                  'InvalidRequestBodyError': 'Argument secotor or org suplied by non-id value !'})

    else:
        abort(400, {'MethodeError': 'Forbidden action'})
