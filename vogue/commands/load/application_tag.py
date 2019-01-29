import logging
import click
import json
from vogue.load.application_tag import load_aplication_tags


LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
LOG = logging.getLogger(__name__)


@click.command("apptag", short_help="Reads database json dump with application tag info.")
@click.option('-d', '--db-dump', type=str, required=True, help='Database dump in json')
@click.pass_context


def application_tags(context, db_dump):
    """Reads list of dicts of application tags as string. eg:
    
        db_dump = '[{'tag':'MELPCFR030', 'category':'wgs',...},...]'
    """

    adapter = context.obj['adapter']

    LOG.info("Reading db json dump.")
    try:
        db_json_list = json.loads(db_dump)
    except:
        LOG.error("Database dump, not in json format.")
        context.abort()

    if not isinstance(db_json_list, list):
        LOG.error("Cannot read input db-dump. Type unknown.")
        context.abort()

    LOG.info("Database json dump is read.")
    load_aplication_tags(adapter, db_json_list)
