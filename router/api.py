"""Rest api endpoint router config"""

from flask import Blueprint, jsonify, request, g, redirect, url_for, abort, current_app, Response
from model import User, UserFileEntry, GeneralFileEntry, dbhelper
from flask_cors import cross_origin
from helper import authentication
from config import db
import sqlalchemy
import platform
import datetime
import flask
import time
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
@api_endpoint.app_errorhandler(404)
@api_endpoint.app_errorhandler(500)
def errorhandler(error):
  return jsonify({"status": error.code, "message": error.description}), error.code

@api_endpoint.app_errorhandler(405)
def errorhandler(error):
  return jsonify({"status": error.code, "message": error.description}), error.code

# server info API
@api_endpoint.route('/api', methods=['GET'])
def server_info():
  sv_info = {
    "flask_ver": flask.__version__,
    "python_ver": platform.sys.version,
    "operating_system": platform.system(),
    "current_timestamp": datetime.datetime.now(),
    "load_time": g.request_time(),
    "environment": os.environ.get('FLASK_ENV')
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
      else:
        abort(401, {'authorizationError': 'Wrong username or password'})

    except KeyError as e:
      abort(401, {'authorizationError': 'Not sufficient or wrong argument given'})

    except sqlalchemy.exc.NoResultFound as e:
      abort(401, {'authorizationError': 'User unavailable'})

@api_endpoint.route('/api/auth/register', methods=["GET","POST"])
# --IMPORTANT --- add this snippet after initial configuration
# @authentication
# def register(current_user):
def register():

  if request.method == 'POST':

    try:
      file_directory = './data/dynamic/{0}-{1}.json'.format(dbhelper.UUIDGenerator(), request.get_json()['org'])
      username = request.get_json()['username']
      password = request.get_json()['password']
      email = request.get_json()['email']
      org = request.get_json()['org']
      lvl = request.get_json()['lvl']

      u = User(email=email, username=username, org=org, lvl=lvl)
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
        "status": "registered",
        "privilege": "admin" if u.lvl == 1 else "cm_moderator"
      }

      return jsonify(send_back)

    except sqlalchemy.exc.IntegrityError as e:
      abort(401, {'UserExistError': 'Account already registered'})

    except KeyError as e:
      abort(401, {'InvalidRequestBodyError': 'Not sufficient or wrong argument given'})

  else:
    abort(401, {'MethodeError': 'Forbidden action'})

# user info API
@api_endpoint.route('/api/user/me', methods=["GET"])
@authentication
def get_me(current_user):
  return jsonify({
    "username" : current_user.username,
    "email": current_user.email,
    "password": "*****",
    "org": current_user.org,
    "privilege": "admin" if current_user.lvl == 1 else "cm_moderator",
    "user_id": current_user.uid
  })

# resource API
@api_endpoint.route('/api/resource', methods=["GET", "POST", "PATCH", "DELETE"])
@authentication
def resource(current_user):
  if request.method == 'GET':
    dyn_fileentry = db.session.query(UserFileEntry.fileURL, User.lvl).join(User).filter(User.uid==current_user.uid).first()
    admin_fileentry = GeneralFileEntry.query.one()
    
    try:

      if dyn_fileentry.lvl == 1:
        with open(admin_fileentry.fileUrl, 'r') as data_content:
          return jsonify(json.load(data_content))

      elif dyn_fileentry.lvl == 2:
        with open(dyn_fileentry.fileURL, 'r') as data_content:
          return jsonify(json.load(data_content))

    except FileNotFoundError:
      abort(404, {'EmptyDataEntry': 'Your data entry is still empty'})

  elif request.method == 'POST':
    if request.headers.get('Content-Type') == 'application/json':
      try:
        dyn_fileentry = db.session.query(UserFileEntry.fileURL, User.lvl).join(User).filter(User.uid==current_user.uid).first()
        dyn_gentry = GeneralFileEntry.query.one()

        if (os.path.isfile(dyn_fileentry.fileURL) and os.path.isfile(dyn_gentry.fileUrl)):
          template = {
            request.get_json()['table_name']: {
              "data": request.get_json()['table_item'],
              "meta":{
                "created_on": time.time(),
                "collection_id": dbhelper.UUIDGenerator(),
                "description": request.get_json()['table_description'],
                  "owner_org": current_user.org,
                  "owner_username": current_user.username
              }
            }
          }

          with open(dyn_fileentry.fileURL, 'r+') as usr_ent:
            a = json.load(usr_ent)
            a.get(current_user.uid).update(template)

            usr_ent.seek(0)
            json.dump(a, usr_ent)

          with open(dyn_gentry.fileUrl, 'r+') as general_ent:
            a = json.load(general_ent)
            a.get(current_user.uid).update(template)
            
            general_ent.seek(0)
            json.dump(a, general_ent)

          return jsonify({"data_saved": True}), 201

        elif (not os.path.isfile(dyn_fileentry.fileURL) and os.path.isfile(dyn_gentry.fileUrl)):
          template = {
            current_user.uid: {
              request.get_json()['table_name']: {
                "data": request.get_json()['table_item'],
                "meta": {
                  "created_on": time.time(),
                  "collection_id": dbhelper.UUIDGenerator(),
                  "description": request.get_json()['table_description'],
                  "owner_org": current_user.org,
                  "owner_username": current_user.username
                }
              }
            }
          }

          with open(dyn_fileentry.fileURL, 'w') as usr_ent:
            json.dump(template, usr_ent)
          
          with open(dyn_gentry.fileUrl, 'r+') as general_ent:
            a = json.load(general_ent)
            a.update(template)
            
            general_ent.seek(0)
            json.dump(a, general_ent)

          return jsonify({"data_saved": True}), 201

        elif (not os.path.isfile(dyn_fileentry.fileURL) and not os.path.isfile(dyn_gentry.fileUrl)):
          template = {
            current_user.uid: {
              request.get_json()['table_name']: {
                "data": request.get_json()['table_item'],
                "meta": {
                  "created_on": time.time(),
                  "collection_id": dbhelper.UUIDGenerator(),
                  "description": request.get_json()['table_description'],
                  "owner_org": current_user.org,
                  "owner_username": current_user.username
                }
              }
            }
          }

          with open(dyn_fileentry.fileURL, 'w') as usr_ent:
            json.dump(template, usr_ent)

          with open(dyn_gentry.fileUrl, 'w') as general_ent:
            json.dump(template, general_ent)

          return jsonify({"data_saved": True}), 201

        else :
          abort(500, {'ServerError': "something went wrong"})

      except KeyError as e:
        abort(401, {'InvalidRequestBodyError': '{0} parameter not Found'.format(e)})

    else:
      abort(400, {'TypeError': 'You submitted non-json body!'})

  elif request.method == 'PATCH':
    if request.headers.get('Content-Type') == 'application/json':
      try:
        g_fe = GeneralFileEntry.query.one()
        u_priv = User.query.filter(User.uid==current_user.uid).one()

        if u_priv.lvl == 1:
          table_name = request.get_json()['table_name']
          table_item = request.get_json()['table_item']
          user = request.get_json()['user_id']
          u_fe = db.session.query(UserFileEntry.fileURL).join(User).filter(User.uid==user).first()

          with open(g_fe.fileUrl, 'r+') as g_edit:
            a = json.load(g_edit)
            a.get(user).get(table_name).update({'data': table_item})
            if (a.get(user).get(table_name).get('meta').get('edited_on')):
              a.get(user).get(table_name).get('meta').update({'edited_on': time.time()})

            elif (not a.get(user).get(table_name).get('meta').get('edited_on')):
              a.get(user).get(table_name).get('meta').update({'edited_on': time.time()})

            g_edit.seek(0)
            json.dump(a, g_edit)

          with open(u_fe.fileURL, 'r+') as uf_edit:
            a = json.load(uf_edit)
            a.get(user).get(table_name).update({'data': table_item})
            
            if (a.get(user).get(table_name).get('meta').get('edited_on')):
              print('ever edited')
              a.get(user).get(table_name).get('meta').update({'edited_on': time.time()})

            elif (not a.get(user).get(table_name).get('meta').get('edited_on')):
              a.get(user).get(table_name).get('meta').update({'edited_on': time.time()})

            uf_edit.seek(0)
            json.dump(a, uf_edit)
          
          return jsonify({"edited": "true"})

        else:
          table_name = request.get_json()['table_name']
          table_item = request.get_json()['table_item']
          u_fe = db.session.query(UserFileEntry.fileURL).join(User).filter(User.uid==current_user.uid).first()

          with open(g_fe.fileUrl, 'r+') as g_edit:
            a = json.load(g_edit)
            a.get(current_user.uid).get(table_name).update({'data': table_item})

            if (a.get(current_user.uid).get(table_name).get('meta').get('edited_on')):
              a.get(current_user.uid).get(table_name).get('meta').update({'edited_on': time.time()})

            elif (not a.get(current_user.uid).get(table_name).get('meta').get('edited_on')):
              a.get(current_user.uid).get(table_name).get('meta').update({'edited_on': time.time()})

            g_edit.seek(0)
            json.dump(a, g_edit)

          with open(u_fe.fileURL, 'r+') as uf_edit:
            a = json.load(uf_edit)
            a.get(current_user.uid).get(table_name).update({'data': table_item})

            if (a.get(current_user.uid).get(table_name).get('meta').get('edited_on')):
              a.get(current_user.uid).get(table_name).get('meta').update({'edited_on': time.time()})

            elif (not a.get(current_user.uid).get(table_name).get('meta').get('edited_on')):
              a.get(current_user.uid).get(table_name).get('meta').update({'edited_on': time.time()})

            uf_edit.seek(0)
            json.dump(a, uf_edit)

          return jsonify({"edited": "true"})
      
      except KeyError as e:
        abort(400, {'InvalidRequestBodyError': '{0} parameter not Found'.format(e)})

    else:
      abort(400, {'TypeError': 'You submitted non-json body!'})

  elif request.method == 'DELETE':
    if request.headers.get('Content-Type') == 'application/json':
      u_priv = User.query.filter(User.uid==current_user.uid).one()
      g_fe = GeneralFileEntry.query.one()

      if u_priv.lvl == 1:
        try:
          user = request.get_json()['user_id']
          table_name = request.get_json()['table_name']
          wich_one = request.get_json()['delete_this']
          u_fe = db.session.query(UserFileEntry.fileURL, User.lvl).join(User).filter(User.uid==user).first()

          with open(g_fe.fileUrl, 'r+') as g_delete:
            x = {'data': []}
            a = json.load(g_delete)
            t = a.get(user).get(table_name).get('data')

            for v in t:
              if v.get(wich_one) != None:
                v.pop(wich_one)

              if len(v) != 0:
                x.get('data').append(v)

            a.get(user).get(table_name).update(x)

            g_delete.seek(0)
            g_delete.truncate()
            json.dump(a, g_delete)

          with open(u_fe.fileURL, 'r+') as uf_delete:
            x = {'data': []}
            a = json.load(uf_delete)
            t = a.get(user).get(table_name).get('data')

            for v in t:
              if v.get(wich_one) != None:
                v.pop(wich_one)

              if len(v) != 0:
                x.get('data').append(v)

            a.get(user).get(table_name).update(x)

            uf_delete.seek(0)
            uf_delete.truncate()
            json.dump(a, uf_delete)

          return jsonify({"deleted": "true admin"})

        except KeyError as e:
          abort(400, {'InvalidRequestBodyError': '{0} parameter not Found'.format(e)})

      else:
        try:
          table_name = request.get_json()['table_name']
          wich_one = request.get_json()['delete_this']

          return jsonify({"deleted": "true"})

        except KeyError as e:
          abort(400, {'InvalidRequestBodyError': '{0} parameter not Found'.format(e)})

    else:
      abort(400, {'TypeError': 'You submitted non-json body!'})

  else:
    abort(405, {'MethodeError': 'Forbidden action'})


@api_endpoint.route('/api/general/resource', methods=["GET"])
def general_r():
  d = dyn_gentry = GeneralFileEntry.query.one()
  try:
    with open(d.fileUrl, 'r') as general_res:
      return jsonify(json.load(general_res))

  except FileNotFoundError as e:
    abort(404, {'EmptyDataEntry': 'Data entry is empty'})

# --IMPORTANT --- remove this snippet after initial configuration
@api_endpoint.route('/api/init_general')
def init_general():
  try:
    test = GeneralFileEntry()
    db.session.add(test)
    db.session.commit()
    return ({"initialized": True})
  except Exception as e:
    print(e)
    abort(500, {'ServerError': "something went wrong"})