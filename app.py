from flask_mongoengine import MongoEngine
from router import api, main_page
from flask_cors import CORS
from flask import Flask
import os

sisv = Flask(__name__)
sisv.config.from_json('./config/flask.config.json')
# CORS(sisv, origins='https://sidakdemo.tapinkab.go.id', vary_header=True)

sisv.register_blueprint(api.api_endpoint)
sisv.register_blueprint(main_page)

with sisv.app_context():
  db = MongoEngine(app=sisv)

if __name__ == '__main__':
  if os.environ.get('FLASK_ENV') == 'production':
    pass

  else:
    os.environ['FLASK_ENV'] = 'development'
    sisv.run(debug=True, port=8000)
