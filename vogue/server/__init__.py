import logging

from flask import Flask
from pymongo import MongoClient
import yaml
import os

from vogue.adapter.plugin import VougeAdapter
from vogue.server.endpoints import (
    covid_blueprint,
    home_blueprint,
    common_trends_blueprint,
    prepps_blueprint,
    sequencing_blueprint,
    qc_blueprint,
    micro_blueprint,
    genotype_blueprint,
    index_blueprint,
)

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
        app.config["DB_NAME"] = os.environ.get("DB_NAME")
        app.config["DB_URI"] = os.environ.get("DB_URI")
        app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
        app.config["DEBUG"] = os.environ.get("DEBUG")
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

    client = MongoClient(app.config["DB_URI"])
    db_name = app.config["DB_NAME"]
    app.client = client
    app.db = client[db_name]
    app.adapter = VougeAdapter(client, db_name=db_name)
    app.register_blueprint(covid_blueprint)
    app.register_blueprint(home_blueprint)
    app.register_blueprint(common_trends_blueprint)
    app.register_blueprint(prepps_blueprint)
    app.register_blueprint(sequencing_blueprint)
    app.register_blueprint(qc_blueprint)
    app.register_blueprint(micro_blueprint)
    app.register_blueprint(genotype_blueprint)
    app.register_blueprint(index_blueprint)

    if app.config["DEBUG"]:
        from flask_debugtoolbar import DebugToolbarExtension

        toolbar = DebugToolbarExtension(app)

    return app
