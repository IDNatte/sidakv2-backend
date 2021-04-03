from router import api, main_page
from flask_cors import CORS
from flask import Flask
from model import User
from config import db
import os

app = Flask(__name__)
app.config.from_json('./config/flask.config.json')
CORS(app)

app.register_blueprint(api.api_endpoint)
app.register_blueprint(main_page)

with app.app_context():
  db.init_app(app)
  db.create_all()

if __name__ == '__main__':
  if os.environ.get('FLASK_ENV') == 'production':
    app.run()

  else:
    os.environ['FLASK_ENV'] = 'development'
    app.run(debug=True, port=8000)
