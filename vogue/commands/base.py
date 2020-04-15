#!/usr/bin/env python
import logging

import click
import coloredlogs
import yaml


from flask.cli import FlaskGroup, with_appcontext
from flask import current_app

# commands
from vogue.commands.load import load as load_command
from vogue.server import create_app, configure_app
from .load import load

# Get version and doc decorator
from vogue import __version__
from vogue.tools.cli_utils import add_doc as doc

LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
LOG = logging.getLogger(__name__)


@click.version_option(__version__)
@click.group(cls=FlaskGroup,
             create_app=create_app,
             add_default_commands=True, 
             invoke_without_command=False,
             add_version_option=False)
@click.option("-c", "--config", type=click.File(), help="Path to config file")
@click.option("-u", "--db-uri", type=str, default='mongodb://localhost:27030', help="Set db uri if no config is provided")
@click.option("-n", "--db-name", type=str, default='vogue-stage', help="Set db name to connect if no config is provided.")
@click.option("-d", "--flask-debug", type=click.Choice(["0", "1"]), default="1", help="Debug mode for Flask if no config is provided.")
@click.option("-s", "--secret-key", type=str, default='hej', help="Secret key for the flask application if no config is provided.")
@with_appcontext
def cli(config, db_uri, db_name, flask_debug, secret_key):
    """ Main entry point """
    if current_app.test:
        return
    if config:
        configure_app(current_app, yaml.safe_load(config))
    else:
        configure_app(current_app, {'DB_URI': db_uri,
                                    'DB_NAME': db_name,
                                    'DEBUG': flask_debug, 
                                    'SECRET_KEY': secret_key}
                        )
    pass


@cli.command()
def test():
    """Test server using CLI"""
    click.echo("test")
    pass


@cli.command()
@with_appcontext
def name():
    """Returns the app name, for testing purposes, mostly"""
    click.echo(current_app.name)
    return current_app.name


cli.add_command(test)
cli.add_command(load)
cli.add_command(name)
