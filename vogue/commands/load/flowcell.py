import logging
import click
from vogue.load.flowcell import load_one, load_all
from flask.cli import with_appcontext, current_app


from genologics.lims import Lims
from genologics.entities import Process
from genologics.config import BASEURI,USERNAME,PASSWORD

LOG = logging.getLogger(__name__)

@click.command("flowcell", short_help = "load flowcell into db.")
@click.option('-r', '--run-id', help = 'Lims process id for the run. Eg: 24-100451')
@click.option('-a', '--all-runs', is_flag = True, help = 'Loads all lims flowcells ids')
@click.option('--dry', is_flag = True, help = 'Load from flowcell or not. (dry-run)')

@with_appcontext
def flowcell(run_id, all_runs, dry):
    """Read and load lims data for a one or all many runs"""
    try:
        lims = Lims(BASEURI,USERNAME,PASSWORD)
    except Exception:
        LOG.warning("Lims connection failed.")
        raise click.Abort()

    if all_runs:
        load_all(current_app.adapter, lims=lims)
        return

    run = Process(lims, id=run_id)
    load_one(current_app.adapter, run = run) 
