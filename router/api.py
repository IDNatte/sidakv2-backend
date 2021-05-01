from flask import Blueprint, jsonify, request, g, abort, current_app, send_from_directory
from model import User, DynamicData, Organization, SectoralGroup, dbhelper
from helper import authentication, allowed_file
from werkzeug import utils
import mongoengine
import datetime
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
@api_endpoint.route('/api/sectoral', methods=["GET", "POST"])
@authentication
def sector_list(current_user):
  if request.method == "GET":
    web_query = request.get_json()
    if web_query:
      sector_query = web_query.get('sector_name')
      sector_list = SectoralGroup.objects(sector_name=sector_query).get()
      return jsonify({"sector_id": sector_list.id, "sector_name": sector_list.sector_name})

    else:
      carrier = []
      sector_list = SectoralGroup.objects

      for x in sector_list:
        paylod = {
          "sector_id": str(x.id),
          "sector_name": x.sector_name
        }

        carrier.append(paylod)
      return jsonify(carrier)

  elif request.method == "POST":
    if current_user.lvl == 1:
      try:
        sector_name = request.get_json()['sector_name']
        sector = SectoralGroup(sector_name=sector_name)
        sector.save()

        return jsonify({ 'sector_created': True })

      except KeyError as e:
        abort(403, {'InvalidRequestBodyError': 'Argument {0} not found in body'.format(e)})

    else:
      abort(401, {'authorizationError': 'Only admin can perform this action !'})

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
          org_list = Organization.objects.filter(id=org_query, sector_group=sector_query).get()      
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
      carrier = []
      org_list = Organization.objects

      for x in org_list:
        payload = {
          "org_id": str(x.id),
          "org_name": x.org_name,
          "org_sector": {
            "sector_id": str(x.sector_group.id),
            "sector_name": x.sector_group.sector_name,
          }
        }

        carrier.append(payload)
      return jsonify(carrier)

  elif request.method == "POST":
    if current_user.lvl == 1:
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
      abort(401, {'authorizationError': 'Only admin can perform this action !'})    

  else:
    abort(400, {'MethodeError': 'Forbidden action'})

@api_endpoint.route('/api/auth/login', methods=["POST"])
def authorization():
  if request.method == "POST":
    try:
      email = request.get_json()['email']
      password = request.get_json()['password']
      
      user_data = User.objects.get(email=email)
      passwd_authentication = dbhelper.check_password(user_data.password, password)

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
      abort(401, {'authorizationError': 'Not sufficient or wrong argument given'})

    except mongoengine.errors.DoesNotExist as e:
      abort(401, {'authorizationError': 'Email not registered'})

  else:
    abort(405, {"MethodeNotAllowed": "Forbidden methode type"})

@api_endpoint.route('/api/auth/register', methods=["GET","POST"])
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
        
        org_search = Organization.objects.filter(id=org, sector_group=sector).count()

        if org_search > 0:

          organization = Organization.objects.filter(id=org, sector_group=sector).get()
          user = User(username=username, email=email, org=organization, lvl=lvl, is_active=bool(is_active))
          user.password = dbhelper.generate_password_hash(password)
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
          abort(403, {'orgListError': 'No organization or sector list registered'})          

      else:
        abort(401, {'authorizationError': 'Only admin can perform this action !'})

    except KeyError as e:
      abort(403, {'InvalidRequestBodyError': 'Argument {0} not found in body'.format(e)})

    except (mongoengine.errors.NotUniqueError):
      abort(403, {'AccountError': 'Account already registered'})

    except mongoengine.errors.ValidationError:
      abort(403, {'InvalidRequestBodyError': 'Argument secotor or org suplied by non-id value !'})

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
    "user_id": str(current_user.id),
    "is_active": current_user.is_active
  })

@api_endpoint.route('/api/user', methods=["GET", "PATCH", "DELETE"])
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
          "organization": x.org.org_name,
          "user_level": "admin" if int(x.lvl) == 1 else "cm_moderator",
          "is_active": x.is_active
        }

        carrier.append(payload)

      return jsonify(carrier)
    else:
      abort(401, {'authorizationError': 'Only admin can see user list!'})

  elif request.method == "PATCH":
    if current_user.lvl == 1:
      try:
        is_activated = request.get_json()['is_active']
        raw_password = request.get_json()['password']
        username = request.get_json()['username']
        user_id = request.get_json()['user_id']
        email = request.get_json()['email']

        user = User.objects(id=user_id).first()
        password = dbhelper.set_password(raw_password)

        user.update(**{"username": username, "password": password, "email": email, "is_active":bool(is_activated)})

        return jsonify({"userUpdated": True})

      except KeyError as e:
        abort(403, {'InvalidRequestBodyError': 'Argument {0} not found in body'.format(e)})

    else:
      abort(401, {'authorizationError': 'Only admin can perform this action !'})

  elif request.method == "DELETE":
    if current_user.lvl == 1:
      try:
        user_id = request.get_json()['user_id']
        user = User.objects(id=user_id).first()
        user.update(**{"is_active": False})

        return jsonify({
          "user_deactivated": True,
          "username": user.username
        })

      except KeyError as e:
        abort(403, {'InvalidRequestBodyError': 'Argument {0} not found in body'.format(e)})

    else:
      abort(401, {'authorizationError': 'Only admin can perform this action !'})

  else:
    abort(405, {"MethodeNotAllowed": "Forbidden methode type"})

@api_endpoint.route('/api/resource', methods=["GET", "POST", "PATCH", "DELETE"])
@authentication
def resource(current_user):
  if request.method == 'GET':
    limit = request.args.get('l')
    skip = request.args.get('s')
    query = request.args.get('q')

    if current_user.lvl == 1:
      if query:
        group_by = request.args.get('group_by')

        if group_by == 'display':
          display_by = request.args.get('display_by')
          
          if display_by == 'chart':
            if skip and limit:
              content = DynamicData.objects(display=display_by).skip(int(skip)).limit(int(limit)).order_by('-created_on')
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
                    "owner_org": x.owner.org.org_name,
                    "owner_id": str(x.owner.id)
                  }
                }

                content_response.append(c_data)
              content_response.sort(key=lambda k: k['created_on'], reverse=True)
              return jsonify(content_response)

            elif skip and not limit:
              content = DynamicData.objects(display=display_by).skip(int(skip)).order_by('-created_on')
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
                    "owner_org": x.owner.org.org_name,
                    "owner_id": str(x.owner.id)
                  }
                }

                content_response.append(c_data)
              content_response.sort(key=lambda k: k['created_on'], reverse=True)
              return jsonify(content_response)

            elif not skip and limit:
              content = DynamicData.objects(display=display_by).limit(int(limit)).order_by('-created_on')
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
                    "owner_org": x.owner.org.org_name,
                    "owner_id": str(x.owner.id)
                  }
                }

                content_response.append(c_data)
              content_response.sort(key=lambda k: k['created_on'], reverse=True)
              return jsonify(content_response)

            else:
              content = DynamicData.objects(display=display_by).order_by('-created_on')
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
                    "owner_org": x.owner.org.org_name,
                    "owner_id": str(x.owner.id)
                  }
                }

                content_response.append(c_data)
              content_response.sort(key=lambda k: k['created_on'], reverse=True)
              return jsonify(content_response)

          elif display_by == 'table':
            if skip and limit:
              content = DynamicData.objects(display=display_by).skip(int(skip)).limit(int(limit)).order_by('-created_on')
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
                    "owner_org": x.owner.org.org_name,
                    "owner_id": str(x.owner.id)
                  }
                }

                content_response.append(c_data)
              content_response.sort(key=lambda k: k['created_on'], reverse=True)
              return jsonify(content_response)

            elif skip and not limit:
              content = DynamicData.objects(display=display_by).skip(int(skip)).order_by('-created_on')
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
                    "owner_org": x.owner.org.org_name,
                    "owner_id": str(x.owner.id)
                  }
                }

                content_response.append(c_data)
              content_response.sort(key=lambda k: k['created_on'], reverse=True)
              return jsonify(content_response)

            elif not skip and limit:
              content = DynamicData.objects(display=display_by).limit(int(limit)).order_by('-created_on')
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
                    "owner_org": x.owner.org.org_name,
                    "owner_id": str(x.owner.id)
                  }
                }

                content_response.append(c_data)
              content_response.sort(key=lambda k: k['created_on'], reverse=True)
              return jsonify(content_response)

            else:
              content = DynamicData.objects(display=display_by).order_by('-created_on')
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
                    "owner_org": x.owner.org.org_name,
                    "owner_id": str(x.owner.id)
                  }
                }

                content_response.append(c_data)
              content_response.sort(key=lambda k: k['created_on'], reverse=True)
              return jsonify(content_response)

          else:
            if skip and limit:
              content = DynamicData.objects().skip(int(skip)).limit(int(limit)).order_by('-created_on')
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
                    "owner_org": x.owner.org.org_name,
                    "owner_id": str(x.owner.id)
                  }
                }

                content_response.append(c_data)
              content_response.sort(key=lambda k: k['created_on'], reverse=True)
              return jsonify(content_response)

            elif skip and not limit:
              content = DynamicData.objects().skip(int(skip)).order_by('-created_on')
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
                    "owner_org": x.owner.org.org_name,
                    "owner_id": str(x.owner.id)
                  }
                }

                content_response.append(c_data)
              content_response.sort(key=lambda k: k['created_on'], reverse=True)
              return jsonify(content_response)

            elif not skip and limit:
              content = DynamicData.objects().limit(int(limit)).order_by('-created_on')
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
                    "owner_org": x.owner.org.org_name,
                    "owner_id": str(x.owner.id)
                  }
                }

                content_response.append(c_data)
              content_response.sort(key=lambda k: k['created_on'], reverse=True)
              return jsonify(content_response)

            else:
              content = DynamicData.objects().order_by('-created_on')
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
                    "owner_org": x.owner.org.org_name,
                    "owner_id": str(x.owner.id)
                  }
                }

                content_response.append(c_data)
              content_response.sort(key=lambda k: k['created_on'], reverse=True)
              return jsonify(content_response)

        else:
          if skip and limit:
            content = DynamicData.objects().skip(int(skip)).limit(int(limit)).order_by('-created_on')
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
                  "owner_org": x.owner.org.org_name,
                  "owner_id": str(x.owner.id)
                }
              }

              content_response.append(c_data)
            content_response.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(content_response)

          elif skip and not limit:
            content = DynamicData.objects().skip(int(skip)).order_by('-created_on')
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
                  "owner_org": x.owner.org.org_name,
                  "owner_id": str(x.owner.id)
                }
              }

              content_response.append(c_data)
            content_response.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(content_response)

          elif not skip and limit:
            content = DynamicData.objects().limit(int(limit)).order_by('-created_on')
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
                  "owner_org": x.owner.org.org_name,
                  "owner_id": str(x.owner.id)
                }
              }

              content_response.append(c_data)
            content_response.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(content_response)

          else:
            content = DynamicData.objects().order_by('-created_on')
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
                  "owner_org": x.owner.org.org_name,
                  "owner_id": str(x.owner.id)
                }
              }

              content_response.append(c_data)
            content_response.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(content_response)

      else:
        if skip and limit:
          content = DynamicData.objects().skip(int(skip)).limit(int(limit)).order_by('-created_on')
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
                "owner_org": x.owner.org.org_name,
                "owner_id": str(x.owner.id)
              }
            }

            content_response.append(c_data)
          content_response.sort(key=lambda k: k['created_on'], reverse=True)
          return jsonify(content_response)

        elif skip and not limit:
          content = DynamicData.objects().skip(int(skip)).order_by('-created_on')
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
                "owner_org": x.owner.org.org_name,
                "owner_id": str(x.owner.id)
              }
            }

            content_response.append(c_data)
          content_response.sort(key=lambda k: k['created_on'], reverse=True)
          return jsonify(content_response)

        elif not skip and limit:
          content = DynamicData.objects().limit(int(limit)).order_by('-created_on')
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
                "owner_org": x.owner.org.org_name,
                "owner_id": str(x.owner.id)
              }
            }

            content_response.append(c_data)
          content_response.sort(key=lambda k: k['created_on'], reverse=True)
          return jsonify(content_response)

        else:
          content = DynamicData.objects().order_by('-created_on')
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
                "owner_org": x.owner.org.org_name,
                "owner_id": str(x.owner.id)
              }
            }

            content_response.append(c_data)
          content_response.sort(key=lambda k: k['created_on'], reverse=True)
          return jsonify(content_response)

    else:
      if query:
        group_by = request.args.get('group_by')

        if group_by == 'display':
          display_by = request.args.get('display_by')

          if display_by == 'chart':
            if skip and limit:
              content = DynamicData.objects(display=display_by, owner=current_user).skip(int(skip)).limit(int(limit)).order_by('-created_on')
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
                    "owner_org": x.owner.org.org_name,
                  }
                }

                content_response.append(c_data)
              content_response.sort(key=lambda k: k['created_on'], reverse=True)
              return jsonify(content_response)

            elif skip and not limit:
              content = DynamicData.objects(display=display_by, owner=current_user).skip(int(skip)).order_by('-created_on')
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
                    "owner_org": x.owner.org.org_name,
                  }
                }

                content_response.append(c_data)
              content_response.sort(key=lambda k: k['created_on'], reverse=True)
              return jsonify(content_response)

            elif not skip and limit:
              content = DynamicData.objects(display=display_by, owner=current_user).limit(int(limit)).order_by('-created_on')
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
                    "owner_org": x.owner.org.org_name,
                  }
                }

                content_response.append(c_data)
              content_response.sort(key=lambda k: k['created_on'], reverse=True)
              return jsonify(content_response)

            else:
              content = DynamicData.objects(display=display_by, owner=current_user).order_by('-created_on')
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
                    "owner_org": x.owner.org.org_name,
                  }
                }

                content_response.append(c_data)
              content_response.sort(key=lambda k: k['created_on'], reverse=True)
              return jsonify(content_response)

          elif display_by == 'table':
            if skip and limit:
              content = DynamicData.objects(display=display_by, owner=current_user).skip(int(skip)).limit(int(limit)).order_by('-created_on')
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
                    "owner_org": x.owner.org.org_name,
                  }
                }

                content_response.append(c_data)
              content_response.sort(key=lambda k: k['created_on'], reverse=True)
              return jsonify(content_response)

            elif skip and not limit:
              content = DynamicData.objects(display=display_by, owner=current_user).skip(int(skip)).order_by('-created_on')
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
                    "owner_org": x.owner.org.org_name,
                  }
                }

                content_response.append(c_data)
              content_response.sort(key=lambda k: k['created_on'], reverse=True)
              return jsonify(content_response)

            elif not skip and limit:
              content = DynamicData.objects(display=display_by, owner=current_user).limit(int(limit)).order_by('-created_on')
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
                    "owner_org": x.owner.org.org_name,
                  }
                }

                content_response.append(c_data)
              content_response.sort(key=lambda k: k['created_on'], reverse=True)
              return jsonify(content_response)

            else:
              content = DynamicData.objects(display=display_by, owner=current_user).order_by('-created_on')
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
                    "owner_org": x.owner.org.org_name,
                  }
                }

                content_response.append(c_data)
              content_response.sort(key=lambda k: k['created_on'], reverse=True)
              return jsonify(content_response)

          else:
            if skip and limit:
              content = DynamicData.objects(owner=current_user).skip(int(skip)).limit(int(limit)).order_by('-created_on')
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
                    "owner_org": x.owner.org.org_name,
                  }
                }

                content_response.append(c_data)
              content_response.sort(key=lambda k: k['created_on'], reverse=True)
              return jsonify(content_response)

            elif skip and not limit:
              content = DynamicData.objects(owner=current_user).skip(int(skip)).order_by('-created_on')
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
                    "owner_org": x.owner.org.org_name,
                  }
                }

                content_response.append(c_data)
              content_response.sort(key=lambda k: k['created_on'], reverse=True)
              return jsonify(content_response)

            elif not skip and limit:
              content = DynamicData.objects(owner=current_user).limit(int(limit)).order_by('-created_on')
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
                    "owner_org": x.owner.org.org_name,
                  }
                }

                content_response.append(c_data)
              content_response.sort(key=lambda k: k['created_on'], reverse=True)
              return jsonify(content_response)

            else:
              content = DynamicData.objects(owner=current_user).order_by('-created_on')
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
                    "owner_org": x.owner.org.org_name,
                  }
                }

                content_response.append(c_data)
              content_response.sort(key=lambda k: k['created_on'], reverse=True)
              return jsonify(content_response)

        else:
          if skip and limit:
            content = DynamicData.objects(owner=current_user).skip(int(skip)).limit(int(limit)).order_by('-created_on')
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
                  "owner_org": x.owner.org.org_name,
                }
              }

              content_response.append(c_data)
            content_response.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(content_response)

          elif skip and not limit:
            content = DynamicData.objects(owner=current_user).skip(int(skip)).order_by('-created_on')
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
                  "owner_org": x.owner.org.org_name,
                }
              }

              content_response.append(c_data)
            content_response.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(content_response)

          elif not skip and limit:
            content = DynamicData.objects(owner=current_user).limit(int(limit)).order_by('-created_on')
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
                  "owner_org": x.owner.org.org_name,
                }
              }

              content_response.append(c_data)
            content_response.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(content_response)

          else:
            content = DynamicData.objects(owner=current_user).order_by('-created_on')
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
                  "owner_org": x.owner.org.org_name,
                }
              }

              content_response.append(c_data)
            content_response.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(content_response)

      else:
        if skip and limit:
          content = DynamicData.objects(owner=current_user).skip(int(skip)).limit(int(limit)).order_by('-created_on')
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
                "owner_org": x.owner.org.org_name,
              }
            }

            content_response.append(c_data)
          content_response.sort(key=lambda k: k['created_on'], reverse=True)
          return jsonify(content_response)

        elif skip and not limit:
          content = DynamicData.objects(owner=current_user).skip(int(skip)).order_by('-created_on')
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
                "owner_org": x.owner.org.org_name,
              }
            }

            content_response.append(c_data)
          content_response.sort(key=lambda k: k['created_on'], reverse=True)
          return jsonify(content_response)

        elif not skip and limit:
          content = DynamicData.objects(owner=current_user).limit(int(limit)).order_by('-created_on')
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
                "owner_org": x.owner.org.org_name,
              }
            }

            content_response.append(c_data)
          content_response.sort(key=lambda k: k['created_on'], reverse=True)
          return jsonify(content_response)

        else:
          content = DynamicData.objects(owner=current_user).order_by('-created_on')
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
                "owner_org": x.owner.org.org_name,
              }
            }

            content_response.append(c_data)
          content_response.sort(key=lambda k: k['created_on'], reverse=True)
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

            table = DynamicData.objects(owner=owner, id=table_id).get()
            if table.display == 'table':
              if len(table.table_content) > 0:
                for x in table.table_content:
                  os.remove(x.get('file_path'))

                table.delete()
                return jsonify({"deleted": True})

              else:
                table.delete()
                return jsonify({"deleted": True})
            else:
              table.delete()
              return jsonify({"deleted": True})

          else:
            owner = current_user
            table_id = request.get_json()['table_id']

            table = DynamicData.objects(owner=owner, id=table_id).get()
            if table.display == 'table':
              if len(table.table_content) > 0:
                for x in table.table_content:
                  os.remove(x.get('file_path'))

                table.delete()
                return jsonify({"deleted": True})

              else:
                table.delete()
                return jsonify({"deleted": True})
            else:
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
            content = DynamicData.objects().filter(id=table_id).get()

            if content.display == 'table':
              for x in content.table_content:
                if x.get('id') == content_id:
                  os.remove(x.get('file_path'))
              
              DynamicData.objects(id=table_id).update(pull__table_content={"id": content_id})

            else:
              DynamicData.objects(id=table_id).update(pull__table_content={"id": content_id})

            return jsonify({"deleted": True})

        except KeyError as e:
          abort(403, {'InvalidRequestBodyError': '{0} parameter not Found'.format(e)})

      else:
        abort(403, {'DeleteEntityError': 'Cannot determine what to delete'})

    except AttributeError as e:
      print(e)
      abort(403, {'DeleteEntityError': 'Cannot determine what to delete'})

    except KeyError as e:
      abort(403, {'InvalidRequestBodyError': '{0} parameter not Found'.format(e)})

  else:
    abort(405, {"MethodeNotAllowed": "Forbidden methode type"})

@api_endpoint.route('/api/resource/upload', methods=["PATCH"])
@authentication
def upload(current_user):
  if request.method == 'PATCH':
    try:
      if current_user.lvl == 1:
        table_id = request.form['table']
        owner = User.objects(id=request.form['owner']).get()
        table = DynamicData.objects(id=table_id).get()
        file = request.files['content']

        if table.display == "table":
          if allowed_file(file.filename):
            filename = utils.secure_filename('{0}-{1}.{2}'.format(time.time(), current_user.org.org_name, file.filename.split('.')[1]))

            new_content = {
              "id": str(dbhelper.BSONObjectID()),
              "content": filename,
              "content_name": file.filename.split('.')[0],
              "file_path": "{0}/{1}".format(current_app.config.get('UPLOAD_FOLDER'), filename),
              "folder_path": current_app.config.get('UPLOAD_FOLDER'),
              "file_url": '/api/public/resource/file/{0}'.format(filename),
              "file_ext": file.filename.split('.')[1]
            }

            DynamicData.objects(owner=owner, id=table_id).update_one(push__table_content=new_content)
            file.save(os.path.join(current_app.config.get('UPLOAD_FOLDER'), filename))
            return jsonify({"fileUploaded": True})

          else:
            abort(403, {"FileExtNotAllowedError": "File extension is not allowed"})

        else:
          abort(403, {"TableError": "Table display type is chart instead of table display"})

      else:
        table_id = request.form['table']
        owner = User.objects(id=current_user.id).get()
        table = DynamicData.objects(id=table_id).get()
        file = request.files['content']

        if table.display == "table":
          if allowed_file(file.filename):
            filename = utils.secure_filename('{0}-{1}.{2}'.format(time.time(), current_user.org.org_name, file.filename.split('.')[1]))
            
            new_content = {
              "id": str(dbhelper.BSONObjectID()),
              "content": filename,
              "content_name": file.filename.split('.')[0],
              "file_path": "{0}/{1}".format(current_app.config.get('UPLOAD_FOLDER'), filename),
              "folder_path": current_app.config.get('UPLOAD_FOLDER'),
              "file_url": '/api/public/resource/file/{0}'.format(filename),
              "file_ext": file.filename.split('.')[1]
            }

            DynamicData.objects(owner=owner, id=table_id).update_one(push__table_content=new_content)
            file.save(os.path.join(current_app.config.get('UPLOAD_FOLDER'), filename))
            return jsonify({"fileUploaded": True})

          else:
            abort(403, {"FileExtNotAllowedError": "File extension is not allowed"})

        else:
          abort(403, {"TableError": "Table display type is chart instead of table display"})

    except KeyError:
      abort(403, {'InvalidRequestBodyError': "Argument 'content' not found in body"})

    except mongoengine.errors.DoesNotExist as e:
      abort(403, {"InputError": str(e)})
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
  query = request.args.get('q')

  if not query:
    limit = request.args.get('l')
    skip = request.args.get('s')

    if skip and limit:
      carrier = []
      table = DynamicData.objects().limit(int(limit)).skip(int(skip)).order_by('-created_on')

      for x in table:
        payload = {
          "table_name": x.table_name,
          "created_on": x.created_on,
          "table_content": x.table_content,
          "display": x.display,
          "table_owner": {
            "username": x.owner.username,
            "organization": x.owner.org.org_name,
            "sector": x.owner.org.sector_group.sector_name
          }
        }
        carrier.append(payload)

      carrier.sort(key=lambda k: k['created_on'], reverse=True)
      return jsonify(carrier)

    elif skip and not limit:
      carrier = []
      table = DynamicData.objects().skip(int(skip)).order_by('-created_on')

      for x in table:
        payload = {
          "table_name": x.table_name,
          "created_on": x.created_on,
          "table_content": x.table_content,
          "display": x.display,
          "table_owner": {
            "username": x.owner.username,
            "organization": x.owner.org.org_name,
            "sector": x.owner.org.sector_group.sector_name
          }
        }
        carrier.append(payload)
      carrier.sort(key=lambda k: k['created_on'], reverse=True)
      return jsonify(carrier)

    elif not skip and limit:
      carrier = []
      table = DynamicData.objects().limit(int(limit)).order_by('-created_on')

      for x in table:
        payload = {
          "table_name": x.table_name,
          "created_on": x.created_on,
          "table_content": x.table_content,
          "display": x.display,
          "table_owner": {
            "username": x.owner.username,
            "organization": x.owner.org.org_name,
            "sector": x.owner.org.sector_group.sector_name
          }
        }
        carrier.append(payload)
      carrier.sort(key=lambda k: k['created_on'], reverse=True)
      return jsonify(carrier)

    else:
      carrier = []
      table = DynamicData.objects().order_by('-created_on')

      for x in table:
        payload = {
          "table_name": x.table_name,
          "created_on": x.created_on,
          "table_content": x.table_content,
          "display": x.display,
          "table_owner": {
            "username": x.owner.username,
            "organization": x.owner.org.org_name,
            "sector": x.owner.org.sector_group.sector_name
          }
        }
        carrier.append(payload)
      carrier.sort(key=lambda k: k['created_on'], reverse=True)
      return jsonify(carrier)

  elif query:
    group_by = request.args.get('group_by')
    limit = request.args.get('l')
    skip = request.args.get('s')

    if group_by == "sector":
      sector_name = request.args.get('sector')

      if limit and skip:
        if sector_name:
          carrier = []
          sector = SectoralGroup.objects(sector_name__iexact=sector_name)
          org = Organization.objects(sector_group__in=sector).all()
          owner = User.objects(org__in=org).all()
          data = DynamicData.objects(owner__in=owner).limit(int(limit)).skip(int(skip)).all().order_by('-created_on')

          for x in data:
            payload = {
              "table_name": x.table_name,
              "created_on": x.created_on,
              "table_content": x.table_content,
              "display": x.display,
              "table_owner": {
                "username": x.owner.username,
                "organization": x.owner.org.org_name,
                "sector": x.owner.org.sector_group.sector_name
              }
            }
            carrier.append(payload)
          carrier.sort(key=lambda k: k['created_on'], reverse=True)
          return jsonify(carrier)

        else:
          carrier = []
          data = DynamicData.objects().limit(int(limit)).skip(int(skip)).order_by('-created_on')

          for x in data:
            payload = {
              "table_name": x.table_name,
              "created_on": x.created_on,
              "table_content": x.table_content,
              "display": x.display,
              "table_owner": {
                "username": x.owner.username,
                "organization": x.owner.org.org_name,
                "sector": x.owner.org.sector_group.sector_name
              }
            }
            carrier.append(payload)
          carrier.sort(key=lambda k: k['created_on'], reverse=True)
          return jsonify(carrier)

      elif not limit and skip:
        if sector_name:
          carrier = []
          sector = SectoralGroup.objects(sector_name__iexact=sector_name)
          org = Organization.objects(sector_group__in=sector).all()
          owner = User.objects(org__in=org).all()
          data = DynamicData.objects(owner__in=owner).skip(int(skip)).all().order_by('-created_on')

          for x in data:
            payload = {
              "table_name": x.table_name,
              "created_on": x.created_on,
              "table_content": x.table_content,
              "display": x.display,
              "table_owner": {
                "username": x.owner.username,
                "organization": x.owner.org.org_name,
                "sector": x.owner.org.sector_group.sector_name
              }
            }
            carrier.append(payload)
          carrier.sort(key=lambda k: k['created_on'], reverse=True)
          return jsonify(carrier)

        else:
          carrier = []
          data = DynamicData.objects().skip(int(skip)).order_by('-created_on')

          for x in data:
            payload = {
              "table_name": x.table_name,
              "created_on": x.created_on,
              "table_content": x.table_content,
              "display": x.display,
              "table_owner": {
                "username": x.owner.username,
                "organization": x.owner.org.org_name,
                "sector": x.owner.org.sector_group.sector_name
              }
            }
            carrier.append(payload)
          carrier.sort(key=lambda k: k['created_on'], reverse=True)
          return jsonify(carrier)

      elif limit and not skip:
        if sector_name:
          carrier = []
          sector = SectoralGroup.objects(sector_name__iexact=sector_name)
          org = Organization.objects(sector_group__in=sector).all()
          owner = User.objects(org__in=org).all()
          data = DynamicData.objects(owner__in=owner).limit(int(limit)).order_by('-created_on')

          for x in data:
            payload = {
              "table_name": x.table_name,
              "created_on": x.created_on,
              "table_content": x.table_content,
              "display": x.display,
              "table_owner": {
                "username": x.owner.username,
                "organization": x.owner.org.org_name,
                "sector": x.owner.org.sector_group.sector_name
              }
            }
            carrier.append(payload)
          carrier.sort(key=lambda k: k['created_on'], reverse=True)
          return jsonify(carrier)

        else:
          carrier = []
          data = DynamicData.objects().limit(int(limit)).order_by('-created_on')

          for x in data:
            payload = {
              "table_name": x.table_name,
              "created_on": x.created_on,
              "table_content": x.table_content,
              "display": x.display,
              "table_owner": {
                "username": x.owner.username,
                "organization": x.owner.org.org_name,
                "sector": x.owner.org.sector_group.sector_name
              }
            }
            carrier.append(payload)
          carrier.sort(key=lambda k: k['created_on'], reverse=True)
          return jsonify(carrier)

      else:
        if sector_name:
          carrier = []
          sector = SectoralGroup.objects(sector_name__iexact=sector_name)
          org = Organization.objects(sector_group__in=sector).all()
          owner = User.objects(org__in=org).all()
          data = DynamicData.objects(owner__in=owner).all().order_by('-created_on')

          for x in data:
            payload = {
              "table_name": x.table_name,
              "created_on": x.created_on,
              "table_content": x.table_content,
              "display": x.display,
              "table_owner": {
                "username": x.owner.username,
                "organization": x.owner.org.org_name,
                "sector": x.owner.org.sector_group.sector_name
              }
            }
            carrier.append(payload)
          carrier.sort(key=lambda k: k['created_on'], reverse=True)
          return jsonify(carrier)

        else:
          carrier = []
          data = DynamicData.objects().order_by('-created_on')

          for x in data:
            payload = {
              "table_name": x.table_name,
              "created_on": x.created_on,
              "table_content": x.table_content,
              "display": x.display,
              "table_owner": {
                "username": x.owner.username,
                "organization": x.owner.org.org_name,
                "sector": x.owner.org.sector_group.sector_name
              }
            }
            carrier.append(payload)
          carrier.sort(key=lambda k: k['created_on'], reverse=True)
          return jsonify(carrier)

    elif group_by == 'display':
      display = request.args.get('display_by')

      if limit and skip:
        if display == 'chart':
          carrier = []
          data = DynamicData.objects(display=display).limit(int(limit)).skip(int(skip)).order_by('-created_on')

          for x in data:
            payload = {
              "table_name": x.table_name,
              "created_on": x.created_on,
              "table_content": x.table_content,
              "display": x.display,
              "table_owner": {
                "username": x.owner.username,
                "organization": x.owner.org.org_name,
                "sector": x.owner.org.sector_group.sector_name
              }
            }
            carrier.append(payload)
          carrier.sort(key=lambda k: k['created_on'], reverse=True)
          return jsonify(carrier)

        elif display == 'table':
          carrier = []
          data = DynamicData.objects(display=display).limit(int(limit)).skip(int(skip)).order_by('-created_on')

          for x in data:
            payload = {
              "table_name": x.table_name,
              "created_on": x.created_on,
              "table_content": x.table_content,
              "display": x.display,
              "table_owner": {
                "username": x.owner.username,
                "organization": x.owner.org.org_name,
                "sector": x.owner.org.sector_group.sector_name
              }
            }
            carrier.append(payload)
          carrier.sort(key=lambda k: k['created_on'], reverse=True)
          return jsonify(carrier)

        else:
          carrier = []
          data = DynamicData.objects().limit(int(limit)).skip(int(skip)).order_by('-created_on')

          for x in data:
            payload = {
              "table_name": x.table_name,
              "created_on": x.created_on,
              "table_content": x.table_content,
              "display": x.display,
              "table_owner": {
                "username": x.owner.username,
                "organization": x.owner.org.org_name,
                "sector": x.owner.org.sector_group.sector_name
              }
            }
            carrier.append(payload)
          carrier.sort(key=lambda k: k['created_on'], reverse=True)
          return jsonify(carrier)

      elif skip and not limit:
        if display == 'chart':
          carrier = []
          data = DynamicData.objects(display=display).skip(int(skip)).order_by('-created_on')

          for x in data:
            payload = {
              "table_name": x.table_name,
              "created_on": x.created_on,
              "table_content": x.table_content,
              "display": x.display,
              "table_owner": {
                "username": x.owner.username,
                "organization": x.owner.org.org_name,
                "sector": x.owner.org.sector_group.sector_name
              }
            }
            carrier.append(payload)
          carrier.sort(key=lambda k: k['created_on'], reverse=True)
          return jsonify(carrier)

        elif display == 'table':
          carrier = []
          data = DynamicData.objects(display=display).skip(int(skip)).order_by('-created_on')

          for x in data:
            payload = {
              "table_name": x.table_name,
              "created_on": x.created_on,
              "table_content": x.table_content,
              "display": x.display,
              "table_owner": {
                "username": x.owner.username,
                "organization": x.owner.org.org_name,
                "sector": x.owner.org.sector_group.sector_name
              }
            }
            carrier.append(payload)
          carrier.sort(key=lambda k: k['created_on'], reverse=True)
          return jsonify(carrier)

        else:
          carrier = []
          data = DynamicData.objects().skip(int(skip)).order_by('-created_on')

          for x in data:
            payload = {
              "table_name": x.table_name,
              "created_on": x.created_on,
              "table_content": x.table_content,
              "display": x.display,
              "table_owner": {
                "username": x.owner.username,
                "organization": x.owner.org.org_name,
                "sector": x.owner.org.sector_group.sector_name
              }
            }
            carrier.append(payload)
          carrier.sort(key=lambda k: k['created_on'], reverse=True)
          return jsonify(carrier)

      elif not skip and limit:
        if display == 'chart':
          carrier = []
          data = DynamicData.objects(display=display).order_by('-created_on').limit(int(limit))

          for x in data:
            payload = {
              "table_name": x.table_name,
              "created_on": x.created_on,
              "table_content": x.table_content,
              "display": x.display,
              "table_owner": {
                "username": x.owner.username,
                "organization": x.owner.org.org_name,
                "sector": x.owner.org.sector_group.sector_name
              }
            }
            carrier.append(payload)
          carrier.sort(key=lambda k: k['created_on'], reverse=True)
          return jsonify(carrier)

        elif display == 'table':
          carrier = []
          data = DynamicData.objects(display=display).limit(int(limit)).order_by('-created_on')

          for x in data:
            payload = {
              "table_name": x.table_name,
              "created_on": x.created_on,
              "table_content": x.table_content,
              "display": x.display,
              "table_owner": {
                "username": x.owner.username,
                "organization": x.owner.org.org_name,
                "sector": x.owner.org.sector_group.sector_name
              }
            }
            carrier.append(payload)
          carrier.sort(key=lambda k: k['created_on'], reverse=True)
          return jsonify(carrier)

        else:
          carrier = []
          data = DynamicData.objects().limit(int(limit)).order_by('-created_on')

          for x in data:
            payload = {
              "table_name": x.table_name,
              "created_on": x.created_on,
              "table_content": x.table_content,
              "display": x.display,
              "table_owner": {
                "username": x.owner.username,
                "organization": x.owner.org.org_name,
                "sector": x.owner.org.sector_group.sector_name
              }
            }
            carrier.append(payload)
          carrier.sort(key=lambda k: k['created_on'], reverse=True)
          return jsonify(carrier)

      else:
        if display == 'chart':
          carrier = []
          data = DynamicData.objects(display=display)

          for x in data:
            payload = {
              "table_name": x.table_name,
              "created_on": x.created_on,
              "table_content": x.table_content,
              "display": x.display,
              "table_owner": {
                "username": x.owner.username,
                "organization": x.owner.org.org_name,
                "sector": x.owner.org.sector_group.sector_name
              }
            }
            carrier.append(payload)
          carrier.sort(key=lambda k: k['created_on'], reverse=True)
          return jsonify(carrier)

        elif display == 'table':
          carrier = []
          data = DynamicData.objects(display=display).order_by('-created_on')

          for x in data:
            payload = {
              "table_name": x.table_name,
              "created_on": x.created_on,
              "table_content": x.table_content,
              "display": x.display,
              "table_owner": {
                "username": x.owner.username,
                "organization": x.owner.org.org_name,
                "sector": x.owner.org.sector_group.sector_name
              }
            }
            carrier.append(payload)
          carrier.sort(key=lambda k: k['created_on'], reverse=True)
          return jsonify(carrier)

        else:
          carrier = []
          data = DynamicData.objects().order_by('-created_on')

          for x in data:
            payload = {
              "table_name": x.table_name,
              "created_on": x.created_on,
              "table_content": x.table_content,
              "display": x.display,
              "table_owner": {
                "username": x.owner.username,
                "organization": x.owner.org.org_name,
                "sector": x.owner.org.sector_group.sector_name
              }
            }
            carrier.append(payload)
          carrier.sort(key=lambda k: k['created_on'], reverse=True)
          return jsonify(carrier)

    elif group_by == 'organization':
      org_name = request.args.get('org')
      display = request.args.get('display')

      if display == 'chart':
        if limit and skip:
          if org_name:
            carrier = []
            org = Organization.objects(org_name__iexact=org_name)
            owner = User.objects(org__in=org).all()
            data = DynamicData.objects(owner__in=owner, display=display).limit(int(limit)).skip(int(skip)).all().order_by('-created_on')

            for x in data:
              payload = {
                "table_name": x.table_name,
                "created_on": x.created_on,
                "table_content": x.table_content,
                "display": x.display,
                "table_owner": {
                  "username": x.owner.username,
                  "organization": x.owner.org.org_name,
                  "sector": x.owner.org.sector_group.sector_name
                }
              }
              carrier.append(payload)
            carrier.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(carrier)

          else:
            carrier = []
            data = DynamicData.objects(display=display).limit(int(limit)).skip(int(skip)).order_by('-created_on')

            for x in data:
              payload = {
                "table_name": x.table_name,
                "created_on": x.created_on,
                "table_content": x.table_content,
                "display": x.display,
                "table_owner": {
                  "username": x.owner.username,
                  "organization": x.owner.org.org_name,
                  "sector": x.owner.org.sector_group.sector_name
                }
              }
              carrier.append(payload)
            carrier.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(carrier)
        
        elif not limit and skip:
          if org_name:
            carrier = []
            org = Organization.objects(org_name__iexact=org_name)
            owner = User.objects(org__in=org).all()
            data = DynamicData.objects(owner__in=owner, display=display).skip(int(skip)).all().order_by('-created_on')

            for x in data:
              payload = {
                "table_name": x.table_name,
                "created_on": x.created_on,
                "table_content": x.table_content,
                "display": x.display,
                "table_owner": {
                  "username": x.owner.username,
                  "organization": x.owner.org.org_name,
                  "sector": x.owner.org.sector_group.sector_name
                }
              }
              carrier.append(payload)
            carrier.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(carrier)

          else:
            carrier = []
            data = DynamicData.objects(display=display).skip(int(skip)).order_by('-created_on')

            for x in data:
              payload = {
                "table_name": x.table_name,
                "created_on": x.created_on,
                "table_content": x.table_content,
                "display": x.display,
                "table_owner": {
                  "username": x.owner.username,
                  "organization": x.owner.org.org_name,
                  "sector": x.owner.org.sector_group.sector_name
                }
              }
              carrier.append(payload)
            carrier.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(carrier)
        
        elif limit and not skip:
          if org_name:
            carrier = []
            org = Organization.objects(org_name__iexact=org_name)
            owner = User.objects(org__in=org).all()
            data = DynamicData.objects(owner__in=owner, display=display).limit(int(limit)).all().order_by('-created_on')

            for x in data:
              payload = {
                "table_name": x.table_name,
                "created_on": x.created_on,
                "table_content": x.table_content,
                "display": x.display,
                "table_owner": {
                  "username": x.owner.username,
                  "organization": x.owner.org.org_name,
                  "sector": x.owner.org.sector_group.sector_name
                }
              }
              carrier.append(payload)
            carrier.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(carrier)

          else:
            carrier = []
            data = DynamicData.objects(display=display).limit(int(limit)).order_by('-created_on')

            for x in data:
              payload = {
                "table_name": x.table_name,
                "created_on": x.created_on,
                "table_content": x.table_content,
                "display": x.display,
                "table_owner": {
                  "username": x.owner.username,
                  "organization": x.owner.org.org_name,
                  "sector": x.owner.org.sector_group.sector_name
                }
              }
              carrier.append(payload)
            carrier.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(carrier)

        else:
          if org_name:
            carrier = []
            org = Organization.objects(org_name__iexact=org_name)
            owner = User.objects(org__in=org).all()
            data = DynamicData.objects(owner__in=owner, display=display).all().order_by('-created_on')

            for x in data:
              payload = {
                "table_name": x.table_name,
                "created_on": x.created_on,
                "table_content": x.table_content,
                "display": x.display,
                "table_owner": {
                  "username": x.owner.username,
                  "organization": x.owner.org.org_name,
                  "sector": x.owner.org.sector_group.sector_name
                }
              }
              carrier.append(payload)
            carrier.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(carrier)

          else:
            carrier = []
            data = DynamicData.objects(display=display).order_by('-created_on')

            for x in data:
              payload = {
                "table_name": x.table_name,
                "created_on": x.created_on,
                "table_content": x.table_content,
                "display": x.display,
                "table_owner": {
                  "username": x.owner.username,
                  "organization": x.owner.org.org_name,
                  "sector": x.owner.org.sector_group.sector_name
                }
              }
              carrier.append(payload)
            carrier.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(carrier)

      elif display == 'table':
        if limit and skip:
          if org_name:
            carrier = []
            org = Organization.objects(org_name__iexact=org_name)
            owner = User.objects(org__in=org).all()
            data = DynamicData.objects(owner__in=owner, display=display).limit(int(limit)).skip(int(skip)).all().order_by('-created_on')

            for x in data:
              payload = {
                "table_name": x.table_name,
                "created_on": x.created_on,
                "table_content": x.table_content,
                "display": x.display,
                "table_owner": {
                  "username": x.owner.username,
                  "organization": x.owner.org.org_name,
                  "sector": x.owner.org.sector_group.sector_name
                }
              }
              carrier.append(payload)
            carrier.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(carrier)

          else:
            carrier = []
            data = DynamicData.objects(display=display).limit(int(limit)).skip(int(skip)).order_by('-created_on')

            for x in data:
              payload = {
                "table_name": x.table_name,
                "created_on": x.created_on,
                "table_content": x.table_content,
                "display": x.display,
                "table_owner": {
                  "username": x.owner.username,
                  "organization": x.owner.org.org_name,
                  "sector": x.owner.org.sector_group.sector_name
                }
              }
              carrier.append(payload)
            carrier.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(carrier)
        
        elif not limit and skip:
          if org_name:
            carrier = []
            org = Organization.objects(org_name__iexact=org_name)
            owner = User.objects(org__in=org).all()
            data = DynamicData.objects(owner__in=owner, display=display).skip(int(skip)).all().order_by('-created_on')

            for x in data:
              payload = {
                "table_name": x.table_name,
                "created_on": x.created_on,
                "table_content": x.table_content,
                "display": x.display,
                "table_owner": {
                  "username": x.owner.username,
                  "organization": x.owner.org.org_name,
                  "sector": x.owner.org.sector_group.sector_name
                }
              }
              carrier.append(payload)
            carrier.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(carrier)

          else:
            carrier = []
            data = DynamicData.objects(display=display).skip(int(skip)).order_by('-created_on')

            for x in data:
              payload = {
                "table_name": x.table_name,
                "created_on": x.created_on,
                "table_content": x.table_content,
                "display": x.display,
                "table_owner": {
                  "username": x.owner.username,
                  "organization": x.owner.org.org_name,
                  "sector": x.owner.org.sector_group.sector_name
                }
              }
              carrier.append(payload)
            carrier.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(carrier)
        
        elif limit and not skip:
          if org_name:
            carrier = []
            org = Organization.objects(org_name__iexact=org_name)
            owner = User.objects(org__in=org).all()
            data = DynamicData.objects(owner__in=owner, display=display).limit(int(limit)).all().order_by('-created_on')

            for x in data:
              payload = {
                "table_name": x.table_name,
                "created_on": x.created_on,
                "table_content": x.table_content,
                "display": x.display,
                "table_owner": {
                  "username": x.owner.username,
                  "organization": x.owner.org.org_name,
                  "sector": x.owner.org.sector_group.sector_name
                }
              }
              carrier.append(payload)
            carrier.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(carrier)

          else:
            carrier = []
            data = DynamicData.objects(display=display).limit(int(limit)).order_by('-created_on')

            for x in data:
              payload = {
                "table_name": x.table_name,
                "created_on": x.created_on,
                "table_content": x.table_content,
                "display": x.display,
                "table_owner": {
                  "username": x.owner.username,
                  "organization": x.owner.org.org_name,
                  "sector": x.owner.org.sector_group.sector_name
                }
              }
              carrier.append(payload)
            carrier.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(carrier)

        else:
          if org_name:
            carrier = []
            org = Organization.objects(org_name__iexact=org_name)
            owner = User.objects(org__in=org).all()
            data = DynamicData.objects(owner__in=owner, display=display).all().order_by('-created_on')

            for x in data:
              payload = {
                "table_name": x.table_name,
                "created_on": x.created_on,
                "table_content": x.table_content,
                "display": x.display,
                "table_owner": {
                  "username": x.owner.username,
                  "organization": x.owner.org.org_name,
                  "sector": x.owner.org.sector_group.sector_name
                }
              }
              carrier.append(payload)
            carrier.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(carrier)

          else:
            carrier = []
            data = DynamicData.objects(display=display).order_by('-created_on')

            for x in data:
              payload = {
                "table_name": x.table_name,
                "created_on": x.created_on,
                "table_content": x.table_content,
                "display": x.display,
                "table_owner": {
                  "username": x.owner.username,
                  "organization": x.owner.org.org_name,
                  "sector": x.owner.org.sector_group.sector_name
                }
              }
              carrier.append(payload)
            carrier.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(carrier)

      else:
        if limit and skip:
          if org_name:
            carrier = []
            org = Organization.objects(org_name__iexact=org_name)
            owner = User.objects(org__in=org).all()
            data = DynamicData.objects(owner__in=owner).limit(int(limit)).skip(int(skip)).all().order_by('-created_on')

            for x in data:
              payload = {
                "table_name": x.table_name,
                "created_on": x.created_on,
                "table_content": x.table_content,
                "display": x.display,
                "table_owner": {
                  "username": x.owner.username,
                  "organization": x.owner.org.org_name,
                  "sector": x.owner.org.sector_group.sector_name
                }
              }
              carrier.append(payload)
            carrier.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(carrier)

          else:
            carrier = []
            data = DynamicData.objects().limit(int(limit)).skip(int(skip)).order_by('-created_on')

            for x in data:
              payload = {
                "table_name": x.table_name,
                "created_on": x.created_on,
                "table_content": x.table_content,
                "display": x.display,
                "table_owner": {
                  "username": x.owner.username,
                  "organization": x.owner.org.org_name,
                  "sector": x.owner.org.sector_group.sector_name
                }
              }
              carrier.append(payload)
            carrier.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(carrier)
        
        elif not limit and skip:
          if org_name:
            carrier = []
            org = Organization.objects(org_name__iexact=org_name)
            owner = User.objects(org__in=org).all()
            data = DynamicData.objects(owner__in=owner).skip(int(skip)).all().order_by('-created_on')

            for x in data:
              payload = {
                "table_name": x.table_name,
                "created_on": x.created_on,
                "table_content": x.table_content,
                "display": x.display,
                "table_owner": {
                  "username": x.owner.username,
                  "organization": x.owner.org.org_name,
                  "sector": x.owner.org.sector_group.sector_name
                }
              }
              carrier.append(payload)
            carrier.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(carrier)

          else:
            carrier = []
            data = DynamicData.objects().skip(int(skip)).order_by('-created_on')

            for x in data:
              payload = {
                "table_name": x.table_name,
                "created_on": x.created_on,
                "table_content": x.table_content,
                "display": x.display,
                "table_owner": {
                  "username": x.owner.username,
                  "organization": x.owner.org.org_name,
                  "sector": x.owner.org.sector_group.sector_name
                }
              }
              carrier.append(payload)
            carrier.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(carrier)
        
        elif limit and not skip:
          if org_name:
            carrier = []
            org = Organization.objects(org_name__iexact=org_name)
            owner = User.objects(org__in=org).all()
            data = DynamicData.objects(owner__in=owner).limit(int(limit)).all().order_by('-created_on')

            for x in data:
              payload = {
                "table_name": x.table_name,
                "created_on": x.created_on,
                "table_content": x.table_content,
                "display": x.display,
                "table_owner": {
                  "username": x.owner.username,
                  "organization": x.owner.org.org_name,
                  "sector": x.owner.org.sector_group.sector_name
                }
              }
              carrier.append(payload)
            carrier.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(carrier)

          else:
            carrier = []
            data = DynamicData.objects().limit(int(limit)).order_by('-created_on')

            for x in data:
              payload = {
                "table_name": x.table_name,
                "created_on": x.created_on,
                "table_content": x.table_content,
                "display": x.display,
                "table_owner": {
                  "username": x.owner.username,
                  "organization": x.owner.org.org_name,
                  "sector": x.owner.org.sector_group.sector_name
                }
              }
              carrier.append(payload)
            carrier.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(carrier)

        else:
          if org_name:
            carrier = []
            org = Organization.objects(org_name__iexact=org_name)
            owner = User.objects(org__in=org).all()
            data = DynamicData.objects(owner__in=owner).all().order_by('-created_on')

            for x in data:
              payload = {
                "table_name": x.table_name,
                "created_on": x.created_on,
                "table_content": x.table_content,
                "display": x.display,
                "table_owner": {
                  "username": x.owner.username,
                  "organization": x.owner.org.org_name,
                  "sector": x.owner.org.sector_group.sector_name
                }
              }
              carrier.append(payload)
            carrier.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(carrier)

          else:
            carrier = []
            data = DynamicData.objects().order_by('-created_on')

            for x in data:
              payload = {
                "table_name": x.table_name,
                "created_on": x.created_on,
                "table_content": x.table_content,
                "display": x.display,
                "table_owner": {
                  "username": x.owner.username,
                  "organization": x.owner.org.org_name,
                  "sector": x.owner.org.sector_group.sector_name
                }
              }
              carrier.append(payload)
            carrier.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(carrier)

    elif group_by == "user":
      username = request.args.get('user')
      display = request.args.get('display')

      if display == 'chart':
        if limit and skip:
          if username:
            carrier = []
            owner = User.objects(username__iexact=username)
            data = DynamicData.objects(owner__in=owner, display=display).limit(int(limit)).skip(int(skip)).all().order_by('-created_on')

            for x in data:
              payload = {
                "table_name": x.table_name,
                "created_on": x.created_on,
                "table_content": x.table_content,
                "display": x.display,
                "table_owner": {
                  "username": x.owner.username,
                  "organization": x.owner.org.org_name,
                  "sector": x.owner.org.sector_group.sector_name
                }
              }
              carrier.append(payload)
            carrier.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(carrier)

          else:
            carrier = []
            data = DynamicData.objects(display=display).limit(int(limit)).skip(int(skip)).order_by('-created_on')

            for x in data:
              payload = {
                "table_name": x.table_name,
                "created_on": x.created_on,
                "table_content": x.table_content,
                "display": x.display,
                "table_owner": {
                  "username": x.owner.username,
                  "organization": x.owner.org.org_name,
                  "sector": x.owner.org.sector_group.sector_name
                }
              }
              carrier.append(payload)
            carrier.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(carrier)

        elif limit and not skip:
          if username:
            carrier = []
            owner = User.objects(username__iexact=username)
            data = DynamicData.objects(owner__in=owner, display=display).limit(int(limit)).all().order_by('-created_on')

            for x in data:
              payload = {
                "table_name": x.table_name,
                "created_on": x.created_on,
                "table_content": x.table_content,
                "display": x.display,
                "table_owner": {
                  "username": x.owner.username,
                  "organization": x.owner.org.org_name,
                  "sector": x.owner.org.sector_group.sector_name
                }
              }
              carrier.append(payload)
            carrier.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(carrier)

          else:
            carrier = []
            data = DynamicData.objects(display=display).limit(int(limit)).order_by('-created_on')

            for x in data:
              payload = {
                "table_name": x.table_name,
                "table_content": x.table_content,
                "display": x.display,
                "table_owner": {
                  "username": x.owner.username,
                  "organization": x.owner.org.org_name,
                  "sector": x.owner.org.sector_group.sector_name
                }
              }
              carrier.append(payload)
            carrier.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(carrier)

        elif not limit and skip:
          if username:
            carrier = []
            owner = User.objects(username__iexact=username)
            data = DynamicData.objects(owner__in=owner, display=display).skip(int(skip)).all().order_by('-created_on')

            for x in data:
              payload = {
                "table_name": x.table_name,
                "created_on": x.created_on,
                "table_content": x.table_content,
                "display": x.display,
                "table_owner": {
                  "username": x.owner.username,
                  "organization": x.owner.org.org_name,
                  "sector": x.owner.org.sector_group.sector_name
                }
              }
              carrier.append(payload)
            carrier.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(carrier)

          else:
            carrier = []
            data = DynamicData.objects(display=display).skip(int(skip)).order_by('-created_on')

            for x in data:
              payload = {
                "table_name": x.table_name,
                "created_on": x.created_on,
                "table_content": x.table_content,
                "display": x.display,
                "table_owner": {
                  "username": x.owner.username,
                  "organization": x.owner.org.org_name,
                  "sector": x.owner.org.sector_group.sector_name
                }
              }
              carrier.append(payload)
            carrier.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(carrier)

        else:
          if username:
            carrier = []
            owner = User.objects(username__iexact=username)
            data = DynamicData.objects(owner__in=owner, display=display).all().order_by('-created_on')

            for x in data:
              payload = {
                "table_name": x.table_name,
                "created_on": x.created_on,
                "table_content": x.table_content,
                "display": x.display,
                "table_owner": {
                  "username": x.owner.username,
                  "organization": x.owner.org.org_name,
                  "sector": x.owner.org.sector_group.sector_name
                }
              }
              carrier.append(payload)
            carrier.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(carrier)

          else:
            carrier = []
            data = DynamicData.objects(display=display).order_by('-created_on')

            for x in data:
              payload = {
                "table_name": x.table_name,
                "created_on": x.created_on,
                "table_content": x.table_content,
                "display": x.display,
                "table_owner": {
                  "username": x.owner.username,
                  "organization": x.owner.org.org_name,
                  "sector": x.owner.org.sector_group.sector_name
                }
              }
              carrier.append(payload)
            carrier.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(carrier)

      elif display == 'table':
        if limit and skip:
          if username:
            carrier = []
            owner = User.objects(username__iexact=username)
            data = DynamicData.objects(owner__in=owner, display=display).limit(int(limit)).skip(int(skip)).all().order_by('-created_on')

            for x in data:
              payload = {
                "table_name": x.table_name,
                "created_on": x.created_on,
                "table_content": x.table_content,
                "display": x.display,
                "table_owner": {
                  "username": x.owner.username,
                  "organization": x.owner.org.org_name,
                  "sector": x.owner.org.sector_group.sector_name
                }
              }
              carrier.append(payload)
            carrier.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(carrier)

          else:
            carrier = []
            data = DynamicData.objects(display=display).limit(int(limit)).skip(int(skip)).order_by('-created_on')

            for x in data:
              payload = {
                "table_name": x.table_name,
                "created_on": x.created_on,
                "table_content": x.table_content,
                "display": x.display,
                "table_owner": {
                  "username": x.owner.username,
                  "organization": x.owner.org.org_name,
                  "sector": x.owner.org.sector_group.sector_name
                }
              }
              carrier.append(payload)
            carrier.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(carrier)

        elif limit and not skip:
          if username:
            carrier = []
            owner = User.objects(username__iexact=username)
            data = DynamicData.objects(owner__in=owner, display=display).limit(int(limit)).all().order_by('-created_on')

            for x in data:
              payload = {
                "table_name": x.table_name,
                "created_on": x.created_on,
                "table_content": x.table_content,
                "display": x.display,
                "table_owner": {
                  "username": x.owner.username,
                  "organization": x.owner.org.org_name,
                  "sector": x.owner.org.sector_group.sector_name
                }
              }
              carrier.append(payload)
            carrier.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(carrier)

          else:
            carrier = []
            data = DynamicData.objects(display=display).limit(int(limit)).order_by('-created_on')

            for x in data:
              payload = {
                "table_name": x.table_name,
                "table_content": x.table_content,
                "display": x.display,
                "table_owner": {
                  "username": x.owner.username,
                  "organization": x.owner.org.org_name,
                  "sector": x.owner.org.sector_group.sector_name
                }
              }
              carrier.append(payload)
            carrier.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(carrier)

        elif not limit and skip:
          if username:
            carrier = []
            owner = User.objects(username__iexact=username)
            data = DynamicData.objects(owner__in=owner, display=display).skip(int(skip)).all().order_by('-created_on')

            for x in data:
              payload = {
                "table_name": x.table_name,
                "created_on": x.created_on,
                "table_content": x.table_content,
                "display": x.display,
                "table_owner": {
                  "username": x.owner.username,
                  "organization": x.owner.org.org_name,
                  "sector": x.owner.org.sector_group.sector_name
                }
              }
              carrier.append(payload)
            carrier.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(carrier)

          else:
            carrier = []
            data = DynamicData.objects(display=display).skip(int(skip)).order_by('-created_on')

            for x in data:
              payload = {
                "table_name": x.table_name,
                "created_on": x.created_on,
                "table_content": x.table_content,
                "display": x.display,
                "table_owner": {
                  "username": x.owner.username,
                  "organization": x.owner.org.org_name,
                  "sector": x.owner.org.sector_group.sector_name
                }
              }
              carrier.append(payload)
            carrier.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(carrier)

        else:
          if username:
            carrier = []
            owner = User.objects(username__iexact=username)
            data = DynamicData.objects(owner__in=owner, display=display).all().order_by('-created_on')

            for x in data:
              payload = {
                "table_name": x.table_name,
                "created_on": x.created_on,
                "table_content": x.table_content,
                "display": x.display,
                "table_owner": {
                  "username": x.owner.username,
                  "organization": x.owner.org.org_name,
                  "sector": x.owner.org.sector_group.sector_name
                }
              }
              carrier.append(payload)
            carrier.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(carrier)

          else:
            carrier = []
            data = DynamicData.objects(display=display).order_by('-created_on')

            for x in data:
              payload = {
                "table_name": x.table_name,
                "created_on": x.created_on,
                "table_content": x.table_content,
                "display": x.display,
                "table_owner": {
                  "username": x.owner.username,
                  "organization": x.owner.org.org_name,
                  "sector": x.owner.org.sector_group.sector_name
                }
              }
              carrier.append(payload)
            carrier.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(carrier)

      else:
        if limit and skip:
          if username:
            carrier = []
            owner = User.objects(username__iexact=username)
            data = DynamicData.objects(owner__in=owner).limit(int(limit)).skip(int(skip)).all().order_by('-created_on')

            for x in data:
              payload = {
                "table_name": x.table_name,
                "created_on": x.created_on,
                "table_content": x.table_content,
                "display": x.display,
                "table_owner": {
                  "username": x.owner.username,
                  "organization": x.owner.org.org_name,
                  "sector": x.owner.org.sector_group.sector_name
                }
              }
              carrier.append(payload)
            carrier.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(carrier)

          else:
            carrier = []
            data = DynamicData.objects().limit(int(limit)).skip(int(skip)).order_by('-created_on')

            for x in data:
              payload = {
                "table_name": x.table_name,
                "created_on": x.created_on,
                "table_content": x.table_content,
                "display": x.display,
                "table_owner": {
                  "username": x.owner.username,
                  "organization": x.owner.org.org_name,
                  "sector": x.owner.org.sector_group.sector_name
                }
              }
              carrier.append(payload)
            carrier.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(carrier)

        elif limit and not skip:
          if username:
            carrier = []
            owner = User.objects(username__iexact=username)
            data = DynamicData.objects(owner__in=owner).limit(int(limit)).all().order_by('-created_on')

            for x in data:
              payload = {
                "table_name": x.table_name,
                "created_on": x.created_on,
                "table_content": x.table_content,
                "display": x.display,
                "table_owner": {
                  "username": x.owner.username,
                  "organization": x.owner.org.org_name,
                  "sector": x.owner.org.sector_group.sector_name
                }
              }
              carrier.append(payload)
            carrier.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(carrier)

          else:
            carrier = []
            data = DynamicData.objects().limit(int(limit)).order_by('-created_on')

            for x in data:
              payload = {
                "table_name": x.table_name,
                "table_content": x.table_content,
                "display": x.display,
                "table_owner": {
                  "username": x.owner.username,
                  "organization": x.owner.org.org_name,
                  "sector": x.owner.org.sector_group.sector_name
                }
              }
              carrier.append(payload)
            carrier.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(carrier)

        elif not limit and skip:
          if username:
            carrier = []
            owner = User.objects(username__iexact=username)
            data = DynamicData.objects(owner__in=owner).skip(int(skip)).all().order_by('-created_on')

            for x in data:
              payload = {
                "table_name": x.table_name,
                "created_on": x.created_on,
                "table_content": x.table_content,
                "display": x.display,
                "table_owner": {
                  "username": x.owner.username,
                  "organization": x.owner.org.org_name,
                  "sector": x.owner.org.sector_group.sector_name
                }
              }
              carrier.append(payload)
            carrier.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(carrier)

          else:
            carrier = []
            data = DynamicData.objects().skip(int(skip)).order_by('-created_on')

            for x in data:
              payload = {
                "table_name": x.table_name,
                "created_on": x.created_on,
                "table_content": x.table_content,
                "display": x.display,
                "table_owner": {
                  "username": x.owner.username,
                  "organization": x.owner.org.org_name,
                  "sector": x.owner.org.sector_group.sector_name
                }
              }
              carrier.append(payload)
            carrier.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(carrier)

        else:
          if username:
            carrier = []
            owner = User.objects(username__iexact=username)
            data = DynamicData.objects(owner__in=owner).all().order_by('-created_on')

            for x in data:
              payload = {
                "table_name": x.table_name,
                "created_on": x.created_on,
                "table_content": x.table_content,
                "display": x.display,
                "table_owner": {
                  "username": x.owner.username,
                  "organization": x.owner.org.org_name,
                  "sector": x.owner.org.sector_group.sector_name
                }
              }
              carrier.append(payload)
            carrier.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(carrier)

          else:
            carrier = []
            data = DynamicData.objects().order_by('-created_on')

            for x in data:
              payload = {
                "table_name": x.table_name,
                "created_on": x.created_on,
                "table_content": x.table_content,
                "display": x.display,
                "table_owner": {
                  "username": x.owner.username,
                  "organization": x.owner.org.org_name,
                  "sector": x.owner.org.sector_group.sector_name
                }
              }
              carrier.append(payload)
            carrier.sort(key=lambda k: k['created_on'], reverse=True)
            return jsonify(carrier)

@api_endpoint.route('/api/public/resource/table/<table_name>')
def table_detail(table_name):
  table = DynamicData.objects(table_name__iexact=table_name).get()
  return jsonify({
    "table_name": table.table_name,
    "created_on": table.created_on,
    "table_content": table.table_content,
    "display": table.display,
    "table_owner": {
      "username": table.owner.username,
      "organization": table.owner.org.org_name,
      "sector": table.owner.org.sector_group.sector_name
    }
  })


@api_endpoint.route('/api/public/resource/file/<filename>')
def file_serve(filename):
  return send_from_directory(current_app.config.get('UPLOAD_FOLDER'), filename)

# helper endpoint
@api_endpoint.route('/api/public/count/<item>')
def general_count(item):
  if item == 'resource':
    group_by = request.args.get('group_by')

    if group_by == 'display':
      display_by = request.args.get('display_by')

      if display_by == 'chart':
        resource = DynamicData.objects(display=display_by).count()
        return jsonify({"item": resource})

      elif display_by == 'table':
        resource = DynamicData.objects(display=display_by).count()
        return jsonify({"item": resource})

      else:
        resource = DynamicData.objects().count()
        return jsonify({"item": resource})


    elif group_by == 'sector':
      sector = request.args.get('sector')
      display = request.args.get('display')

      if display == 'chart':
        if sector:
          sector = SectoralGroup.objects(sector_name__iexact=sector)
          org = Organization.objects(sector_group__in=sector).all()
          owner = User.objects(org__in=org).all()
          resource = DynamicData.objects(owner__in=owner, display=display).count()
          return jsonify({"item": resource})

        else:
          resource = DynamicData.objects(display=display).count()
          return jsonify({"item": resource})

      elif display == 'table':
        if sector:
          sector = SectoralGroup.objects(sector_name__iexact=sector)
          org = Organization.objects(sector_group__in=sector).all()
          owner = User.objects(org__in=org).all()
          resource = DynamicData.objects(owner__in=owner, display=display).count()
          return jsonify({"item": resource})

        else:
          resource = DynamicData.objects(display=display).count()
          return jsonify({"item": resource})

      else:
        if sector:
          sector = SectoralGroup.objects(sector_name__iexact=sector)
          org = Organization.objects(sector_group__in=sector).all()
          owner = User.objects(org__in=org).all()
          resource = DynamicData.objects(owner__in=owner).count()
          return jsonify({"item": resource})

        else:
          resource = DynamicData.objects().count()
          return jsonify({"item": resource})

    elif group_by == 'organization':
      org_name = request.args.get('org')
      display = request.args.get('display')

      if display == 'chart':
        if org_name:
          org = Organization.objects(org_name__iexact=org_name)
          owner = User.objects(org__in=org).all()
          resource = DynamicData.objects(owner__in=owner, display=display).count()
          return jsonify({"item": resource})

        else:
          resource = DynamicData.objects(display=display).count()
          return jsonify({"item": resource})

      elif display == 'table':
        if org_name:
          org = Organization.objects(org_name__iexact=org_name)
          owner = User.objects(org__in=org).all()
          resource = DynamicData.objects(owner__in=owner, display=display).count()
          return jsonify({"item": resource})

        else:
          resource = DynamicData.objects(display=display).count()
          return jsonify({"item": resource})

      else:
        if org_name:
          org = Organization.objects(org_name__iexact=org_name)
          owner = User.objects(org__in=org).all()
          resource = DynamicData.objects(owner__in=owner).count()
          return jsonify({"item": resource})

        else:
          resource = DynamicData.objects().count()
          return jsonify({"item": resource})

    elif group_by == 'user':
      username = request.args.get('user')
      display = request.args.get('display')

      if display == 'chart':
        if username:
          owner = User.objects(username__iexact=username)
          resource = DynamicData.objects(owner__in=owner, display=display).count()
          return jsonify({"item": resource})

        else:
          resource = DynamicData.objects(display=display).count()
          return jsonify({"item": resource})

      elif display == 'table':
        if username:
          owner = User.objects(username__iexact=username)
          resource = DynamicData.objects(owner__in=owner, display=display).count()
          return jsonify({"item": resource})

        else:
          resource = DynamicData.objects(display=display).count()
          return jsonify({"item": resource})

      else:
        if username:
          owner = User.objects(username__iexact=username)
          resource = DynamicData.objects(owner__in=owner).count()
          return jsonify({"item": resource})

        else:
          resource = DynamicData.objects().count()
          return jsonify({"item": resource})

    else:
      resource = DynamicData.objects().count()
      return jsonify({"item": resource})

  else:
    abort(400, {"CountError": "Missing direction on what to count"})
