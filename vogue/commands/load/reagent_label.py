import logging
import click
from vogue.load.reagent_label import load_one, load_all, load_recent
from datetime import date, timedelta


LOG = logging.getLogger(__name__)


@click.command("reagent_labels", short_help="Load reagent_labels into db.")
@click.option(
    "-a",
    "--all-reagent_labels",
    is_flag=True,
    help="Loads reagent_labels from all flowcells found in LIMS.",
)
@click.option("--dry", is_flag=True, help="Load reagent_labels from flowcell or not. (dry-run)")
@click.option(
    "-d",
    "--days",
    type=int,
    help="Update only reagent_labels from runs updated in the latest number of days",
)
@click.pass_context
def reagent_labels(ctx: click.Context, all_reagent_labels, dry, days):
    """Read and load lims data for a one or all many reagent_labels"""
    adapter = ctx.obj["adapter"]
    lims = ctx.obj["lims"]
    if not lims:
        LOG.warning("Lims connection failed.")
        raise click.Abort()

    if days:
        try:
            some_days_ago = date.today() - timedelta(days=days)
            the_date = some_days_ago.strftime("%Y-%m-%dT00:00:00Z")
        except Exception as err:
            LOG.error(err)
            raise click.Abort()
        load_recent(adapter, lims, the_date)
    elif all_reagent_labels:
        load_all(adapter, lims=lims)
