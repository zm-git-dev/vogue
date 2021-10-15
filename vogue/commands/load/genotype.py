import logging
import click
from vogue.load.genotype import load_sample

LOG = logging.getLogger(__name__)


@click.command("genotype", short_help="Load genotype document into db.")
@click.option("-s", "--sample-doc", help="Dictionary with genotype data.")
@click.pass_context
def genotype(ctx: click.Context, sample_doc):
    """Reads data from the genotype database collection and parses out plot specific data on sample
    level to put into the genotype_analysis colleciton"""
    adapter = ctx.obj["adapter"]

    if sample_doc:
        load_sample(adapter, sample_doc)
        return
