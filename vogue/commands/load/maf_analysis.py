import logging
import click
from vogue.load.maf_analysis import load_one, load_many
from flask.cli import with_appcontext, current_app

LOG = logging.getLogger(__name__)

@click.command("maf_analysis", 
                short_help = "Load maf_analysis into db.")
@click.option('-s', '--sample-id', 
                help = 'Load sample with specific lims sample id.')
@click.option('-d', '--date', 
                help = 'Update only samples added to the genotype database after date')

@with_appcontext
def maf_analysis(date, sample_id):
    """Reads data from the genotype database collection and parses out plot specific data on sample 
    level to put into the maf_analysis colleciton"""

    if date:
        load_many(current_app.adapter, date)
        return
    
    if sample_id:
        load_one(current_app.adapter, case_id = case_id)
        return
