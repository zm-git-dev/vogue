import logging
import click
from vogue.load.reagent_label_category import load_all
from flask.cli import with_appcontext, current_app
from datetime import date, timedelta

from vogue.constants.constants import RUN_TYPES

LOG = logging.getLogger(__name__)


@click.command("reagent_label_categories", short_help="Load reagent_labels into db.")
@click.option(
    "-c",
    "--categories",
    multiple=True,
    type=str,
    help="Loads all reagent_label cathegories from lims.",
)
@with_appcontext
def reagent_label_categories(categories: list = None):
    """Read and load reagent_label categories from lims"""

    if not current_app.lims:
        LOG.warning("Lims connection failed.")
        raise click.Abort()
    lims = current_app.lims
    load_all(adapter=current_app.adapter, lims=lims, categories=categories)
