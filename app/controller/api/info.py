"""API info blueprint"""


from app.helper.csrf import paranoid_mode
from flask import Blueprint, jsonify, g
import datetime
import time

api_endpoint = Blueprint('info_api', __name__)


@api_endpoint.app_errorhandler(400)
@api_endpoint.app_errorhandler(500)
def errorhandler(error):
    return jsonify({"status": error.code, "message": error.description}), error.code


@api_endpoint.before_app_request
def before_request():
    g.request_start_time = time.time()
    g.request_time = lambda: "%.5fs" % (time.time() - g.request_start_time)


@api_endpoint.after_app_request
def after_request(response):
    return paranoid_mode(response)


@api_endpoint.route('/api/status', methods=['GET'])
def server_info():
    sv_info = {
        "current_timestamp": datetime.datetime.now(),
        "load_time": g.request_time(),
        "API_Version": "1.1.3",
        "Backend_Version": "1.3"
    }

    return jsonify(sv_info)
