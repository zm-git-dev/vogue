import logging
import click
from vogue.load.sample_analysis import load_one, load_all
from flask.cli import with_appcontext, current_app

LOG = logging.getLogger(__name__)

@click.command("sample_analysis", short_help = "Load sample_analysis into db.")
@click.option('-s', '--sample-id', help = 'Lims sample id.')
@click.option('-a', '--all_samples', is_flag = True, help = 'Loads all samples found in the case_analysis collection.')
@click.option('--dry', is_flag = True, help = 'Load from flowcell or not. (dry-run)')

@with_appcontext
def sample_analysis(sample_id, all_samples, dry):
    """Reads data from the case_analysis collection and parses out plot specific data on sample 
    level to put into the sample_analysis colleciton"""

    if all_samples:
        load_all(current_app.adapter)
        return

    load_one(current_app.adapter, sample_id = sample_id) 