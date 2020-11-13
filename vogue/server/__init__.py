import os
import logging

from flask import Flask
from pymongo import MongoClient
import yaml

from vogue.adapter.plugin import VougeAdapter
from vogue.server.views import blueprint

from genologics.lims import Lims
from genologics.config import BASEURI, USERNAME, PASSWORD

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)


def create_app(test=False):
    app = Flask(__name__)
    app.test = test
    if test:
        return app

    try:
        app.config.from_envvar('VOGUE_CONFIG')
        configure_app(app)
    except:
        pass

    return app


def configure_app(app, config=None):
    try:
        app.lims = Lims(BASEURI, USERNAME, PASSWORD)
    except:
        app.lims = None

    if config:
        app.config = {**app.config, **yaml.safe_load(config)}

    client = MongoClient(app.config['DB_URI'])
    db_name = app.config['DB_NAME']
    app.client = client
    app.db = client[db_name]
    app.adapter = VougeAdapter(client, db_name=db_name)
    app.register_blueprint(blueprint)

    if app.config['DEBUG'] == 1:
        from flask_debugtoolbar import DebugToolbarExtension
        toolbar = DebugToolbarExtension(app)

    return app
