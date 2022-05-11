"""CSRF Protection Helper"""

from flask import make_response
import json


def paranoid_mode(response):
    with open('./app/config/flask.config.json', 'r') as config:
        read_config = json.load(config)

        response.headers['Vary'] = read_config.get('VARY')
        response.headers['X-POWERED-BY'] = read_config.get('XPB')
        response.headers['X-Frame-Options'] = read_config.get('XFO')
        response.headers['X-XSS-Protection'] = read_config.get('XSSP')
        response.headers['Content-Security-Policy'] = read_config.get('CSP')
        response.headers['X-Content-Type-Options'] = read_config.get('XCTPO')
        response.headers['Access-Control-Allow-Headers'] = read_config.get(
            'HEADERS')
        response.headers['Access-Control-Allow-Origin'] = read_config.get(
            'ORIGIN')

        return response
