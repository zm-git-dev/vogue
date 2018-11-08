#!/usr/bin/env python
import logging

import click
import coloredlogs

# commands
from vogue.commands.load import load as load_command

# Get version and doc decorator
from vogue import __version__
from vogue.tools.cli_utils import add_doc as doc

LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
LOG = logging.getLogger(__name__)

@click.group()
@click.version_option(version=__version__)
@click.option('--loglevel',
    default='INFO',
    type=click.Choice(LOG_LEVELS),
    help="Set the level of log output.",
    show_default=True,
)
@click.pass_context
@doc("Vogue {version}: A trending package".format(version=__version__))
def cli(context, loglevel):
    coloredlogs.install(log_level=loglevel)

cli.add_command(load_command)
