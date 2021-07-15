"""Common router config"""
from flask import Blueprint, render_template
import platform
import os

static_url_path = ('/static')
static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates/')
main_endpoint = Blueprint('main_endpoint', __name__, template_folder=template_folder, static_folder=static_folder)

@main_endpoint.after_request
def add_header(response):
  response.headers['X-Powered-By'] = 'Python {0}'.format(platform.python_version())

  return response

@main_endpoint.app_errorhandler(404)
def error_4xx(error):
  return render_template('error/4xx.html', error=error), error.code

@main_endpoint.app_errorhandler(500)
def errorhandler(error):
  return render_template('error/5xx.html', error=error), error.code


@main_endpoint.route('/')
def index():
  return render_template('index.html')