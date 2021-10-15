import logging
import click
from vogue.load.reagent_label_category import load_all
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
@click.pass_context
def reagent_label_categories(ctx: click.Context, categories: list = None):
    """Read and load reagent_label categories from lims"""
    adapter = ctx.obj["adapter"]
    lims = ctx.obj["lims"]
    if not lims:
        LOG.warning("Lims connection failed.")
        raise click.Abort()
    lims = lims
    load_all(adapter=adapter, lims=lims, categories=categories)
