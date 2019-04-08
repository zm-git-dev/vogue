import logging
import click
from vogue.load.sample import load_one, load_all, load_one_dry, load_all_dry
from flask.cli import with_appcontext, current_app
from datetime import datetime


from genologics.entities import Sample


LOG = logging.getLogger(__name__)

@click.command("sample", short_help = "load sample/samples into db.")
@click.option('-s', '--sample-lims-id', 
                help = 'Input sample lims id')
@click.option('-m', '--many', is_flag = True, 
                help = 'Loads all lims samples if no other options are selected')
@click.option('--dry', is_flag = True, 
                help = 'Load from sample or not. (dry-run)')
@click.option('-f', '--load-from', 
                help = 'load from this sample lims id. Use if load all broke. Start where it ended')
@click.option('-n', '--new', is_flag = True,
                help = 'Use this flagg if you only want to load samples that dont exist in the database')
@click.option('-d', '--date', 
                help = 'Update only samples delivered after date')
@with_appcontext
def sample(sample_lims_id, dry, many, load_from, new, date):
    """Read and load lims data for one ore all samples. When loading many smaples,
    the different options -f, -n, -d are used to delimit the subset of samples to load."""
    
    if not current_app.lims:
        LOG.warning("Lims connection failed.")
        raise click.Abort()

    lims = current_app.lims
        
    if date:
        try:
            date = datetime.strptime(date, "%y%m%d").date()
        except Exception as err:
            LOG.error(err)
            raise click.Abort()

    if many:
        if dry:
            load_all_dry()
        else:
            load_all(current_app.adapter, lims=lims, start_sample=load_from, new_only=new, date=date)
    else:
        lims_sample = Sample(lims, id = sample_lims_id)
        if not lims_sample:
            LOG.critical("The sample does not exist in the database in the LIMS database.")
            raise SyntaxError()
        if dry:
            load_one_dry(lims_sample)
        else:
            load_one(current_app.adapter, lims_sample , lims=lims, new_only=new, date = date)



