import logging
import click
from vogue.load.flowcell import load_one, load_all, load_recent
from datetime import date, timedelta

from vogue.constants.constants import RUN_TYPES

LOG = logging.getLogger(__name__)


@click.command("flowcell", short_help="Load flowcell into db.")
@click.option("-r", "--run-id", help="Run id for the run. Eg: 190510_A00689_0032_BHJLW2DSXX")
@click.option("-a", "--all-runs", is_flag=True, help="Loads all flowcells found in LIMS.")
@click.option("--dry", is_flag=True, help="Load from flowcell or not. (dry-run)")
@click.option(
    "-d", "--days", type=int, help="Update only runs updated in the latest number of days"
)
@click.pass_context
def flowcell(ctx: click.Context, run_id, all_runs, dry, days):
    """Read and load lims data for a one or all many runs"""
    adapter = ctx.obj["adapter"]
    lims = ctx.obj["lims"]
    if not lims:
        LOG.warning("Lims connection failed.")
        raise click.Abort()

    lims = lims

    if days:
        try:
            some_days_ago = date.today() - timedelta(days=days)
            the_date = some_days_ago.strftime("%Y-%m-%dT00:00:00Z")
        except Exception as err:
            LOG.error(err)
            raise click.Abort()
        load_recent(adapter, lims, the_date)
    elif all_runs:
        load_all(adapter, lims=lims)
    elif run_id:
        runs = []
        for run_type in RUN_TYPES:
            runs.extend(lims.get_processes(udf={"Run ID": run_id}, type=run_type))
        if runs == []:
            LOG.warning("There is no run with this Run ID")
            raise click.Abort()
        if len(runs) > 1:
            LOG.warning("There is more than one run with this run ID. Picking the latest")
            run = runs[-1]
        else:
            run = runs[0]
        load_one(adapter, run=run)
