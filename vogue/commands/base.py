#!/usr/bin/env python
import logging

import click
import coloredlogs

from flask.cli import FlaskGroup, with_appcontext
from flask import current_app

# commands
from vogue.commands.load import load as load_command
from vogue.server import create_app
from .load import load

# Get version and doc decorator
from vogue import __version__
from vogue.tools.cli_utils import add_doc as doc

LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
LOG = logging.getLogger(__name__)

cli = FlaskGroup(create_app=create_app)

@click.group()
def test():
    """Test server using CLI"""
    click.echo("test")
    pass

@click.command()
@click.option('-y', '--year', default=2019)
@click.option('-k', '--group_key', default=None)
@with_appcontext
def aggregate(year, group_key):
    from vogue.constants.constants import MONTHS, COLORS
    "Run aggregation pipeline"
    y_vals = ['received_to_delivered', 'received_to_prepped', 'prepped_to_sequenced', 'sequenced_to_delivered']
    adapter = current_app.adapter
    data = list(adapter.aggregate_group_month(year, y_vals, group_key))
    

    for y_val in y_vals:
        results = {}
        i = 0
        for a in data: 
            group = a['_id'][group_key]
            month = a['_id']['month']
            value = a[y_val]
            if group not in results:
                results[group] = {'data' : [None]*12,
                                                'color' : COLORS[i]}
            results[group]['data'][month -1] = value
        print(results)



@cli.command()
@with_appcontext
def name():
    """Returns the app name, for testing purposes, mostly"""
    click.echo(current_app.name)
    return current_app.name

cli.add_command(test)
cli.add_command(load)
cli.add_command(aggregate)
test.add_command(name)