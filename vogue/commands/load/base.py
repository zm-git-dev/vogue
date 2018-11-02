#!/usr/bin/env python
import click

# commands
from vogue.commands.load.analysis import analysis as analysis_command
from vogue.commands.load.lims import lims as lims_command

# Get version and doc decorator
from vogue import __version__
from vogue.tools.cli_utils import add_doc as doc

@click.group()
@click.version_option(version=__version__)
@click.pass_context

@doc("Vogue {version}: A trending package".format(version=__version__))
def load(context):
    pass

load.add_command(analysis_command)
load.add_command(lims_command)
