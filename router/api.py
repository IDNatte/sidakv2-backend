from flask import Blueprint, jsonify, request, g, abort, current_app
from model import User, DynamicData, Organization, SectoralGroup, dbhelper
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
        sector = request.get_json()['sector']
        org = request.get_json()['org']
        lvl = request.get_json()['lvl']

        sectoral = SectoralGroup.objects(sector_name=sector).get()
        organization = Organization.objects(sector_group=sectoral, org_name=org).get()

        user = User(username=username, email=email, org=org, lvl=lvl)
        user.password = dbhelper.generate_password_hash(password)
        user.save()

        send_back = {
          "user_id": str(user.id),
          "username": str(user.username),
          "email": str(user.email),
          "password": "protected",
          "org": str(user.org.org_name),
          "status": "registered",
          "privilege": "admin" if int(user.lvl) == 1 else "cm_moderator"
        }

        return jsonify(send_back)

      else:
        abort(401, {'authorizationError': 'Only admin can registering new user !'})

    except KeyError as e:
      abort(403, {'InvalidRequestBodyError': 'Argument {0} not found in body'.format(e)})

    except (mongoengine.errors.NotUniqueError) as e:
      print(e)
      abort(403, {'AccountError': 'Account already registered'})

  else:
    abort(400, {'MethodeError': 'Forbidden action'})

# protected endpoint
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

@api_endpoint.route('/api/sectoral', methods=["GET", "POST"])
@authentication
def sector_list(current_user):
  if request.method == "GET":
    web_query = request.get_json()
    if web_query:
      sector_query = web_query.get('sector_name')
      sector_list = SectoralGroup.objects(sector_name=sector_query).get()
      return jsonify(sector_list)

    else:
      sector_list = SectoralGroup.objects
      return jsonify(sector_list)

  elif request.method == "POST":
    try:
      sector_name = request.get_json()['sector_name']
      sector = SectoralGroup(sector_name=sector_name)
      sector.save()

      return jsonify({ 'sector_created': True })

    except KeyError as e:
      abort(403, {'InvalidRequestBodyError': 'Argument {0} not found in body'.format(e)})

  else:
    abort(405, {"MethodeNotAllowed": "Forbidden methode type"})

@api_endpoint.route('/api/org', methods=["GET", "POST"])
@authentication
def org_list(current_user):
  if request.method == "GET":
    web_query = request.get_json()
    if web_query:
      sector_query = web_query.get('sector_id')
      org_query = web_query.get('org_name')

      try:
        if sector_query and org_query:
          org_list = Organization.objects.filter(id=org_query, sector_group=sector_query)      
          return jsonify(org_list)

        elif not sector_query and org_query:
          org_list = Organization.objects.filter(org_name=org_query).get()
          return jsonify(org_list)

        elif sector_query and not org_query:
          org_list = Organization.objects.filter(sector_group=sector_query)      
          return jsonify(org_list)

        else:
          abort(403, {'InvalidRequestBodyError': 'Argument org_name or sector_id not found in body'})

      except mongoengine.errors.ValidationError:
        abort(403, {'InvalidRequestBodyError': 'Mixed parameter in body founded'})

    else:
      org_list = Organization.objects
      return jsonify(org_list)

  elif request.method == "POST":
    try:
      sector_id = request.get_json()['sector_id']
      org_name = request.get_json()['org_name']
      sector = SectoralGroup.objects(id=sector_id).get()
      org = Organization(org_name=org_name, sector_group=sector)
      org.save()

      return jsonify({"organization_created": True})

    except KeyError as e:
      abort(403, {'InvalidRequestBodyError': 'Argument {0} not found in body'.format(e)})

  else:
    abort(400, {'MethodeError': 'Forbidden action'})

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
          "display": x.display,
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
          "display": x.display,
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
      display = request.get_json()['display']

      table = DynamicData(owner=current_user, table_name=table_name, table_desc=table_desc, display=display, table_content=table_content)
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

# general endpoint
@api_endpoint.route('/api/public/sectoral')
def general_sect():
  carrier = []
  sector = SectoralGroup.objects()

  for x in sector:
    print(x.sector_name)
    payload = {
      "sector_id": str(x.id),
      "sector_name": x.sector_name
    }
    carrier.append(payload)
  return jsonify(carrier)

@api_endpoint.route('/api/public/org')
def general_org():
  carrier = []
  org = Organization.objects()

  for x in org:
    payload = {
      "org_id": str(x.id),
      "org_name": x.org_name,
      "sector": {
        "sector_id": str(x.sector_group.id),
        "sector_name": x.sector_group.sector_name
      }
    }
    carrier.append(payload)
  return jsonify(carrier)

@api_endpoint.route('/api/public/resource')
def general_res():
  carrier = []
  table = DynamicData.objects()

  for x in table:
    payload = {
      "table_name": x.table_name,
      "table_content": x.table_content,
      "display": x.display,
      "table_owner": {
        "username": x.owner.username,
        "organization": x.owner.org
      }
    }
    carrier.append(payload)
  return jsonify(carrier)
