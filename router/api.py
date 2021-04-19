from flask import Blueprint, jsonify, request, g, abort, current_app
from model import User, DynamicData , dbhelper
from helper import authentication
import mongoengine
import datetime
import time
import jwt

api_endpoint = Blueprint('api_endpoint', __name__)

@api_endpoint.before_app_request
def before_request():
  g.request_start_time = time.time()
  g.request_time = lambda: "%.5fs" %(time.time() - g.request_start_time)

# error handler API
@api_endpoint.app_errorhandler(400)
@api_endpoint.app_errorhandler(401)
@api_endpoint.app_errorhandler(403)
@api_endpoint.app_errorhandler(404)
@api_endpoint.app_errorhandler(405)
@api_endpoint.app_errorhandler(500)
@api_endpoint.app_errorhandler(501)
def errorhandler(error):
  return jsonify({"status": error.code, "message": error.description}), error.code

# server info API
@api_endpoint.route('/api', methods=['GET'])
def server_info():
  sv_info = {
    "current_timestamp": datetime.datetime.now(),
    "load_time": g.request_time(),
    "API_Version": "1.1.2",
    "Backend_Version": "1.2"
  }

  return jsonify(sv_info)

# authorization API
@api_endpoint.route('/api/auth/login', methods=["POST"])
def authorization():
  if request.method == "POST":
    try:
      email = request.get_json()['email']
      password = request.get_json()['password']
      
      user_data = User.objects.get(email=email)
      passwd_authentication = dbhelper.check_password(user_data.password, password)

      if passwd_authentication:
        token_exp = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        token = jwt.encode({
          "carrier": {
            "uid": str(user_data.id)
          },
          'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1), 
        }, current_app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({"access_token": token.decode('UTF-8'), "expired": token_exp})
      else:
        abort(401, {'authorizationError': 'Wrong password'})

    except KeyError as e:
      abort(401, {'authorizationError': 'Not sufficient or wrong argument given'})

    except mongoengine.errors.DoesNotExist as e:
      abort(401, {'authorizationError': 'Email not registered'})

@api_endpoint.route('/api/auth/register', methods=["GET","POST"])
@authentication
def register(current_user):
  if request.method == 'POST':
    try:
      if current_user.lvl == 1:
        username = request.get_json()['username']
        password = request.get_json()['password']
        email = request.get_json()['email']
        org = request.get_json()['org']
        lvl = request.get_json()['lvl']

        user = User(username=username, email=email, org=org, lvl=lvl)
        user.password = dbhelper.generate_password_hash(password)
        user.save()

        send_back = {
          "user_id": str(user.id),
          "username": str(user.username),
          "email": str(user.email),
          "password": "protected",
          "org": str(user.org),
          "status": "registered",
          "privilege": "admin" if int(user.lvl) == 1 else "cm_moderator"
        }

        return jsonify(send_back)

      else:
        abort(401, {'authorizationError': 'Only admin can registering new user !'})

    except KeyError as e:
      abort(403, {'InvalidRequestBodyError': 'Argument {0} not found in body'.format(e)})

    except (mongoengine.errors.NotUniqueError) as e:
      abort(403, {'AccountError': 'Account already registered'})

  else:
    abort(400, {'MethodeError': 'Forbidden action'})

@api_endpoint.route('/api/user/me', methods=["GET"])
@authentication
def get_me(current_user):
  return jsonify({
    "username" : str(current_user.username),
    "email": str(current_user.email),
    "password": "*****",
    "org": str(current_user.org),
    "privilege": "admin" if int(current_user.lvl) == 1 else "cm_moderator",
    "user_id": str(current_user.id)
  })

@api_endpoint.route('/api/user', methods=["GET"])
@authentication
def user_list(current_user):
  if request.method == "GET":
    carrier = []
    if current_user.lvl == 1:
      user = User.objects()
      for x in user:
        payload = {
          "user_id": str(x.id),
          "username": x.username,
          "password": "protected",
          "organization": x.org,
          "user_level": "admin" if int(x.lvl) == 1 else "cm_moderator"
        }

        carrier.append(payload)

      return jsonify(carrier)
    else:
      abort(401, {'authorizationError': 'Only admin can see user list!'})
  else:
    abort(405, {"MethodeNotAllowed": "Forbidden methode type"})

@api_endpoint.route('/api/resource', methods=["GET", "POST", "PATCH", "DELETE"])
@authentication
def resource(current_user):
  if request.method == 'GET':
    if current_user.lvl == 1:
      content = DynamicData.objects()
      content_response = []
      for x in content:
        c_data = {
          "table_id": str(x.id),
          "created_on": x.created_on,
          "table_name": x.table_name,
          "table_description": x.table_desc,
          "table_content": x.table_content,
          "owner" : {
            "owner_name": x.owner.username,
            "owner_org": x.owner.org,
            "owner_id": str(x.owner.id)
          }
        }

        content_response.append(c_data)

      return jsonify(content_response)
    else:
      content = DynamicData.objects(owner=current_user)
      content_response = []
      for x in content:
        c_data = {
          "table_id": str(x.id),
          "created_on": x.created_on,
          "table_name": x.table_name,
          "table_description": x.table_desc,
          "table_content": x.table_content,
          "owner" : {
            "owner_name": x.owner.username,
            "owner_org": x.owner.org,
          }
        }

        content_response.append(c_data)
      return jsonify(content_response)

  elif request.method == 'POST':
    try:
      table_name = request.get_json()['table_name']
      table_desc = request.get_json()['table_description']
      table_content = request.get_json()['table_content']

      table = DynamicData(owner=current_user, table_name=table_name, table_desc=table_desc, table_content=table_content)
      table.save()

      return ({'created': True})

    except mongoengine.errors.NotUniqueError as e:
      abort(403, {'InvalidRequestBodyError': 'Table name already exists'})
    except KeyError as e:
      abort(403, {'InvalidRequestBodyError': '{0} parameter not Found'.format(e)})

  elif request.method == 'PATCH':
    try:
      if current_user.lvl == 1:
        owner = request.get_json()['owner']
        table_id = request.get_json()['table_id']
        new_content = request.get_json()['table_content']
        new_content.update({"id": str(dbhelper.BSONObjectID())})

        DynamicData.objects(owner=owner, id=table_id).update_one(push__table_content=new_content)
        return ({"edited": True})

      else:
        owner = current_user
        table_id = request.get_json()['table_id']
        new_content = request.get_json()['table_content']
        new_content.update({"id": str(dbhelper.BSONObjectID())})

        DynamicData.objects(owner=owner, id=table_id).update_one(push__table_content=new_content)
        return ({"edited": True})

    except KeyError as e:
      abort(403, {'InvalidRequestBodyError': '{0} parameter not Found'.format(e)})


  elif request.method == 'DELETE':
    try:
      req = request.get_json()
      table_delete = req.get('is_table')
      content_delete = req.get('is_content')

      if table_delete and not content_delete:
        try:
          if current_user.lvl == 1:
            owner = request.get_json()['owner']
            table_id = request.get_json()['table_id']

            table = DynamicData.objects(owner=owner, id=table_id)
            table.delete()

            return jsonify({"deleted": True})

          else:
            owner = current_user
            table_id = request.get_json()['table_id']

            table = DynamicData.objects(owner=owner, id=table_id)
            table.delete()

            return jsonify({"deleted": True})

        except KeyError as e:
          abort(403, {'InvalidRequestBodyError': '{0} parameter not Found'.format(e)})

      elif not table_delete and content_delete:
        try:
          if current_user == 1:
            owner = request.get_json()['owner']
            table_id = request.get_json()['table_id']
            content_id = request.get_json()['content_id']

            DynamicData.objects(owner=owner, id=table_id).update(pull__table_content={"id": content_id})
            return jsonify({"deleted": True})

          else:
            owner = current_user
            table_id = request.get_json()['table_id']
            content_id = request.get_json()['content_id']
            
            DynamicData.objects(id=table_id).update(pull__table_content={"id": content_id})
            return jsonify({"deleted": True})

        except KeyError as e:
          abort(403, {'InvalidRequestBodyError': '{0} parameter not Found'.format(e)})

      else:
        abort(403, {'DeleteEntityError': 'Cannot determine what to delete'})

    except AttributeError as e:
      abort(403, {'DeleteEntityError': 'Cannot determine what to delete'})

    except KeyError as e:
      abort(403, {'InvalidRequestBodyError': '{0} parameter not Found'.format(e)})

  else:
    abort(405, {"MethodeNotAllowed": "Forbidden methode type"})

@api_endpoint.route('/api/public/resource')
def general_res():
  carrier = []
  table = DynamicData.objects()

  for x in table:
    payload = {
      "table_name": x.table_name,
      "table_content": x.table_content,
      "table_owner": {
        "username": x.owner.username,
        "organization": x.owner.org
      }
    }
    carrier.append(payload)

  return jsonify(carrier)
