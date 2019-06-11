#!/usr/bin/env python
import logging

import click

from mongo_adapter import get_client
from vogue.adapter import VougeAdapter

LOG = logging.getLogger(__name__)

# commands
from vogue.commands.load.case_analysis import analysis as analysis_command
from vogue.commands.load.application_tag import application_tags as status_db_command
from vogue.commands.load.flowcell import flowcell as flowcell_command
from vogue.commands.load.sample import sample as sample_command

# Get version and doc decorator
from vogue import __version__
from vogue.tools.cli_utils import add_doc as doc

@click.group()
@click.version_option(version=__version__)
@doc("Vogue {version}: A trending package".format(version=__version__))
def load():
    """Main entry point of load commands"""
    pass



load.add_command(analysis_command)
load.add_command(status_db_command)
load.add_command(sample_command)
load.add_command(flowcell_command)

