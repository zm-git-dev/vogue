import logging
import click
from vogue.load.index_category import load_all
from flask.cli import with_appcontext, current_app
from datetime import date, timedelta

from vogue.constants.constants import RUN_TYPES

LOG = logging.getLogger(__name__)

@click.command("index_categories", short_help = "Load indexes into db.")
@click.option('-a', '--all-indexes', is_flag = True, help = 'Loads all index cathegories from lims.')


@with_appcontext
def index_categories(all_indexes):
    """Read and load index categories from lims"""

    if not current_app.lims:
        LOG.warning("Lims connection failed.")
        raise click.Abort()

    lims = current_app.lims
    load_all(current_app.adapter, lims=lims)
