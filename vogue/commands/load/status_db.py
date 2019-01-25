import logging
import click
import json
from vogue.tools.cli_utils import json_read
from vogue.tools.cli_utils import check_file

LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
LOG = logging.getLogger(__name__)


@click.command("statusdb", short_help="Reads status-db json dump.")

@click.option(
    '-d',
    '--db-dump',
    type=str,
    required=True,
    help='Database dump in json')

@click.option(
    '-n',
    '--db-name',
    required=True,
    help='Database name')

@click.pass_context

def status_db(context, db_dump, db_name):
    """Reads status-db json dump"""

    LOG.info("Reading db json dump.")
    try:
        db_dict = json.loads(db_dump)
    except FileNotFoundError as e:
        context.abort()

    db_dict = json.loads(db_dump)
    if not isinstance(db_dict, dict):
        LOG.error("Cannot read input db-dump. Type unknown.")
        context.abort()

    LOG.info("db config is read....")
