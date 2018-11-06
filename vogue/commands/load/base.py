#!/usr/bin/env python
import click

from mongo_adapter import get_client
from vogue.adapter.adapter import VougeAdapter
import sys

# commands
from vogue.commands.load.analysis import analysis as analysis_command
from vogue.commands.load.lims import lims as lims_command

# Get version and doc decorator
from vogue import __version__
from vogue.tools.cli_utils import add_doc as doc

@click.group()
@click.version_option(version=__version__)
@click.option('-d', '--database-name', default = 'trending', show_default = True, 
                help = 'Database name')
@click.option('-u', '--database-uri', default = "mongodb://localhost:27017", 
                show_default = True, help = 'Database uri')
@click.pass_context

@doc("Vogue {version}: A trending package".format(version=__version__))
def load(context, database_name, database_uri):
    context.obj = {}
    try:
        client = get_client(uri = database_uri)
    except Exception as err:
        sys.exit(f'Invalid database uri: {err}')
    adapter = VougeAdapter(client, db_name=database_name)
    context.obj['adapter'] = adapter

    

load.add_command(analysis_command)
load.add_command(lims_command)
