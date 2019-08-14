import logging
import click
from vogue.load.maf_analysis import load_one, load_many, load_all
from flask.cli import with_appcontext, current_app

LOG = logging.getLogger(__name__)

@click.command("maf_analysis", 
                short_help = "Load maf_analysis into db.")
@click.option('-s', '--sample-id', 
                help = 'Load sample with specific lims sample id.')
@click.option('-a', '--all_samples', is_flag = True,
                help = 'Load all sample in the genotype database')
@click.option('-d', '--days', type=click.INT,
                help = 'Update only samples that were added to the genotype database a specific number of days ago.')

@with_appcontext
def maf_analysis(days, sample_id, all_samples):
    """Reads data from the genotype database collection and parses out plot specific data on sample 
    level to put into the maf_analysis colleciton"""

    if days:
        load_many(current_app.adapter, days)
        return
    
    if sample_id:
        load_one(current_app.adapter, sample_id = sample_id)
        return

    if all_samples:
        load_all(current_app.adapter)
        return        
