import logging
import click
from vogue.load.reagent_label_category import load_all
from flask.cli import with_appcontext, current_app
from datetime import date, timedelta

from vogue.constants.constants import RUN_TYPES

LOG = logging.getLogger(__name__)

@click.command("reagent_label_categories", short_help = "Load reagent_labels into db.")
@click.option('-a', '--all-reagent_labels', is_flag = True, help = 'Loads all reagent_label cathegories from lims.')


@with_appcontext
def reagent_label_categories(all_reagent_labels):
    """Read and load reagent_label categories from lims"""

    if not current_app.lims:
        LOG.warning("Lims connection failed.")
        raise click.Abort()

    lims = current_app.lims
    load_all(current_app.adapter, lims=lims)
