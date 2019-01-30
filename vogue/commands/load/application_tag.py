import logging
import click
import json
from vogue.load.application_tag import load_aplication_tags

LOG = logging.getLogger(__name__)


@click.command("apptag", short_help="Reads json with application tag info.")
@click.option('-a', '--application-tags', type=str, required=True, help='Database dump in json')
#@click.argument('application-tags', type=str, help='json formatted application tags')
@click.pass_context


def application_tags(context, application_tags):
    """Reads list of dicts of application tags as string. eg:
    
        application_tags = '[{'tag':'MELPCFR030', 'category':'wgs',...},...]'
    """

    adapter = context.obj['adapter']

    LOG.info("Reading json.")
    try:
        json_list = json.loads(application_tags)
    except:
        LOG.error("This is not json.")
        context.abort()

    if not isinstance(json_list, list):
        LOG.error("Cannot read input. Its not json.")
        context.abort()

    LOG.info("json is read.")
    load_aplication_tags(adapter, json_list)
