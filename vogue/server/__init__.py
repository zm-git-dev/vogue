import os
from pymongo import MongoClient
import logging
from flask import Flask
from vogue.adapter.plugin import VougeAdapter

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)

def create_app(test = False):
    #configuration files are relative to the instance folder
    app = Flask(__name__, instance_relative_config=True)
    if not test:
        app.config.from_pyfile('config.py')

        client = MongoClient(app.config['DB_URI'])
        db_name = app.config['DB_NAME']
        app.client = client
        app.db = client[db_name]
        app.adapter = VougeAdapter(client, db_name = db_name)

    return app
