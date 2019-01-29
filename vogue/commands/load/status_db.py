import logging
import click
import json
from vogue.load.status_db import load_aplication_tags


LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
LOG = logging.getLogger(__name__)


@click.command("statusdb", short_help="Reads status-db json dump.")
@click.option('-d', '--db-dump', type=str, required=True, help='Database dump in json')
@click.option('-a', '--app-tag',  is_flag=True, help='Loading to application tag collection.')
@click.pass_context


def status_db(context, db_dump, app_tag):
    """Reads status-db json dump"""

    adapter = context.obj['adapter']

    LOG.info("Reading db json dump.")
    try:
        db_json_list = json.loads(db_dump)
    except:
        LOG.error("status-db dump, not in json format.")
        context.abort()

    if not isinstance(db_json_list, list):
        LOG.error("Cannot read input db-dump. Type unknown.")
        context.abort()

    LOG.info("db status-db json dump is read.")

    
    if app_tag:
        load_aplication_tags(adapter, db_json_list)
