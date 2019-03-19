import logging
import click
from vogue.load.sample import load_one, load_all, load_one_dry, load_all_dry
from flask.cli import with_appcontext, current_app


from genologics.lims import Lims
from genologics.entities import Sample
from genologics.config import BASEURI,USERNAME,PASSWORD

LOG = logging.getLogger(__name__)

@click.command("lims", short_help = "load lims into db.")
@click.option('-s', '--sample-lims-id', 
                help = 'Input sample lims id')
@click.option('-a', '--all-samples', is_flag = True, 
                help = 'Loads all lims sample ids')
@click.option('--dry', is_flag = True, 
                help = 'Load from sample or not. (dry-run)')
@click.option('-f', '--load-from', 
                help = 'load from this sample lims id. Use if load all broke. Start where it ended')
@click.option('-n', '--new_only', is_flag = True,
                help = 'Use this flagg if you only want to load samples that dont exist in the database')
@click.option('-d', '--date', 
                help = 'Update only samples delivered after date')
@with_appcontext
def lims(sample_lims_id, dry, all_samples, load_from, new_only, date):
    """Read and load lims data for a given sample id"""
    try:
        lims = Lims(BASEURI,USERNAME,PASSWORD)
    except Exception:
        LOG.warning("Lims connection failed.")
        raise click.Abort()

    if all_samples:
        if dry:
            load_all_dry()
        else:
            load_all(current_app.adapter, lims=lims, start_sample=load_from, new_only=new_only, date=date)
    else:
        lims_sample = Sample(lims, id = sample_lims_id)
        if not lims_sample:
            LOG.critical("The sample does not exist in the database in the LIMS database.")
            raise SyntaxError()
        if dry:
            load_one_dry(lims_sample)
        else:
            load_one(current_app.adapter, lims_sample , lims=lims, new_only=new_only, date = date)



