import logging
import click
from vogue.load.genotype import load_sample
from flask.cli import with_appcontext, current_app

LOG = logging.getLogger(__name__)


@click.command("genotype", short_help="Load genotype document into db.")
@click.option("-s", "--sample-doc", help="Dictionary with genotype data.")
@with_appcontext
def genotype(sample_doc):
    """Reads data from the genotype database collection and parses out plot specific data on sample
    level to put into the genotype_analysis colleciton"""
    if sample_doc:
        load_sample(current_app.adapter, sample_doc)
        return
