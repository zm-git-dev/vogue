#!/usr/bin/env python
import logging

import click
from genologics.lims import Lims

from vogue.settings import get_vogue_adapter, get_lims

LOG = logging.getLogger(__name__)

# commands
from vogue.commands.load.bioinfo import bioinfo as bioinfo_command
from vogue.commands.load.application_tag import application_tags as status_db_command
from vogue.commands.load.flowcell import flowcell as flowcell_command
from vogue.commands.load.sample import sample as sample_command
from vogue.commands.load.genotype import genotype as genotype_command
from vogue.commands.load.reagent_label import reagent_labels as reagent_label_command
from vogue.commands.load.reagent_label_category import (
    reagent_label_categories as reagent_label_category_command,
)

# Get version and doc decorator
from vogue import __version__
from vogue.tools.cli_utils import add_doc as doc


@click.group()
@click.version_option(version=__version__)
@click.pass_context
@doc("Vogue {version}: A trending package".format(version=__version__))
def load(ctx):
    """Main entry point of load commands"""

    ctx.ensure_object(dict)
    ctx.obj["lims"] = get_lims()
    ctx.obj["adapter"] = get_vogue_adapter()


load.add_command(bioinfo_command)
load.add_command(status_db_command)
load.add_command(sample_command)
load.add_command(flowcell_command)
load.add_command(genotype_command)
load.add_command(reagent_label_command)
load.add_command(reagent_label_category_command)
