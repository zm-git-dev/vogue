import os
from pymongo import MongoClient
import logging
from flask import Flask
from .extentions import adapter

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)

def create_app():
    #configuration files are relative to the instance folder
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('config.py')

    client = MongoClient(app.config['DB_URI'])
    app.client = client
    app.db = client[app.config['DB_NAME']]
    app.adapter = adapter

    app.register_blueprint(blueprint)
    return app


from .views import blueprint