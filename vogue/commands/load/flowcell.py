import logging
import click
from vogue.load.flowcell import load_one, load_all
from flask.cli import with_appcontext, current_app


from genologics.lims import Lims
from genologics.entities import Sample
from genologics.config import BASEURI,USERNAME,PASSWORD

LOG = logging.getLogger(__name__)

@click.command("flowcell", short_help = "load flowcell into db.")
@click.option('-r', '--run-id', help = 'Input flowcell run id')
@click.option('-a', '--all-runs', is_flag = True, help = 'Loads all lims flowcells ids')
@click.option('--dry', is_flag = True, help = 'Load from flowcell or not. (dry-run)')
@with_appcontext
def lims(run_id, all_runs, dry):
    """Read and load lims data for a given sample id"""
    try:
        lims = Lims(BASEURI,USERNAME,PASSWORD)
    except Exception:
        LOG.warning("Lims connection failed.")
        raise click.Abort()

    if all_runs:
        load_all(current_app.adapter, lims=lims)
        return

    load_one_sample(current_app.adapter, run_id, lims=lims)
