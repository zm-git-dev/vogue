import logging
import click
from vogue.load.sample import load_one, load_all, load_recent, load_one_dry, load_all_dry
from datetime import date, timedelta

from genologics.entities import Sample

LOG = logging.getLogger(__name__)


@click.command("sample", short_help="load sample/samples into db.")
@click.option("-s", "--sample-lims-id", help="Input sample lims id")
@click.option(
    "-a",
    "--all_samples",
    is_flag=True,
    help="Loads all lims samples if no other options are selected",
)
@click.option(
    "-f",
    "--load-from",
    help="Use together with --all_samples. Load from this sample lims id. Use if load all broke. Start where it ended",
)
@click.option(
    "-d", "--days", type=int, help="Update only samples updated in the latest number of days"
)
@click.option("--dry", is_flag=True, help="Load from sample or not. (dry-run)")
@click.pass_context
def sample(ctx: click.Context, sample_lims_id, all_samples, load_from, days, dry):
    """Read and load lims data for one sample, all samples or the most recently updated samples."""
    adapter = ctx.obj["adapter"]
    lims = ctx.obj["lims"]

    if not lims:
        LOG.warning("Lims connection failed.")
        raise click.Abort()

    lims = lims

    if days:
        some_days_ago = date.today() - timedelta(days=days)
        the_date = some_days_ago.strftime("%Y-%m-%dT00:00:00Z")
        load_recent(adapter, lims, the_date)
    elif all_samples:
        if dry:
            load_all_dry()
        else:
            load_all(adapter, lims=lims, start_sample=load_from)
    elif sample_lims_id:
        lims_sample = Sample(lims, id=sample_lims_id)
        if not lims_sample:
            LOG.critical("The sample does not exist in the database in the LIMS database.")
            raise SyntaxError()
        if dry:
            load_one_dry(lims_sample)
        else:
            load_one(adapter, lims_sample, lims=lims)
