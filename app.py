from router.api import api_endpoint
from router import main_page

from flask import Flask, request
from model import User
from config import db

import os

app = Flask(__name__)
app.config.from_json('flask.config.json')

app.register_blueprint(api_endpoint)
app.register_blueprint(main_page)

with app.app_context():
  db.init_app(app)
  db.create_all();

if __name__ == '__main__':
  app.run(debug=True)

