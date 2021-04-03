"""Common router config"""

from flask import Blueprint, render_template
import os

template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates/')
static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
static_url_path = ('/static')
main_page = Blueprint('main_page', __name__, template_folder=template_folder, static_folder=static_folder)

@main_page.app_errorhandler(404)
def error_4xx(error):
  return render_template('error/4xx.html', error=error)

@main_page.app_errorhandler(500)
def error_5xx(error):
  return render_template('error/5xx.html', error=error)


@main_page.route('/')
def index():
  return render_template('index.html')
  