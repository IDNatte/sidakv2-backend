from flask_mongoengine import MongoEngine
from flask import Flask
import json

from app.controller.api import public_resource, protected_resource, auth, info
from app.core.script import populate, admin
from app.controller.web import home
from app.shared import DB


def init_app(test_config=None):
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_file('./config/flask.config.json', load=json.load)

    # initialize database
    DB.init_app(app)
    populate.init_populator(app)
    admin.init_admin(app)

    # API blueprint
    app.register_blueprint(info.api_endpoint)
    app.register_blueprint(auth.api_endpoint)
    app.register_blueprint(public_resource.api_endpoint)
    app.register_blueprint(protected_resource.api_endpoint)

    # Web service blueprint
    app.register_blueprint(home.home_endpoint)

    # testing

    return app
