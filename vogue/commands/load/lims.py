import logging
import click
from vogue.load.sample import load_one_sample, load_all_samples
from flask.cli import with_appcontext, current_app


from genologics.lims import Lims
from genologics.entities import Sample
from genologics.config import BASEURI,USERNAME,PASSWORD

LOG = logging.getLogger(__name__)

@click.command("lims", short_help = "load lims into db.")
@click.option('-s', '--sample-lims-id', help = 'Input sample lims id')
@click.option('--load-all', is_flag = True, help = 'Loads all lims sample ids')
@click.option('--dry', is_flag = True, help = 'Load from sample or not. (dry-run)')
@click.option('-f', '--load-from', 
                help = 'load from this sample lims id. Use if load all broke. Start where it ended')
@with_appcontext
def lims(sample_lims_id, dry, load_all, load_from):
    """Read and load lims data for a given sample id"""
    try:
        lims = Lims(BASEURI,USERNAME,PASSWORD)
    except Exception:
        LOG.warning("Lims connection failed.")
        raise click.Abort()

    if load_all:
        load_all_samples(current_app.adapter, lims=lims, dry_run=dry, start_sample=load_from)
        return

    load_one_sample(current_app.adapter, sample_lims_id, lims=lims, dry_run=dry)
