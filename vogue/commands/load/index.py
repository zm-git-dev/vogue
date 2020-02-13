import logging
import click
from vogue.load.index import load_one, load_all, load_recent
from flask.cli import with_appcontext, current_app
from datetime import date, timedelta

from vogue.constants.constants import RUN_TYPES

LOG = logging.getLogger(__name__)

@click.command("indexes", short_help = "Load indexes into db.")
@click.option('-a', '--all-indexes', is_flag = True, help = 'Loads indexes from all flowcells found in LIMS.')
@click.option('--dry', is_flag = True, help = 'Load indexes from flowcell or not. (dry-run)')
@click.option('-d', '--days', type = int,
                help = 'Update only indexes from runs updated in the latest number of days')

@with_appcontext
def indexes(all_indexes, dry, days):
    """Read and load lims data for a one or all many indexes"""

    if not current_app.lims:
        LOG.warning("Lims connection failed.")
        raise click.Abort()

    lims = current_app.lims

    if days:
        try:
            some_days_ago = date.today() - timedelta(days=days) 
            the_date = some_days_ago.strftime("%Y-%m-%dT00:00:00Z")
        except Exception as err:
            LOG.error(err)
            raise click.Abort()
        load_recent(current_app.adapter,lims, the_date)
    elif all_indexes:
        load_all(current_app.adapter, lims=lims)
