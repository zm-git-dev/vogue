import logging
import click
import json
from vogue.load.application_tag import load_aplication_tags

LOG = logging.getLogger(__name__)


@click.command("apptag", short_help="Reads json with application tag info.")
@click.option('-a', '--application-tags', required=True, help='json formatted application tags')
@click.pass_context


def application_tags(context, application_tags: list):
    """Reads list of dicts of application tags as string. eg:
    
        Args: 
            application_tags(list(dict)): '[{'tag':'MELPCFR030', 'category':'wgs',...},...]'
            context:
    """

    adapter = context.obj['adapter']

    LOG.info("Reading json.")
    try:
        json_list = json.loads(application_tags)
    except json.JSONDecodeError as e: 
        LOG.error("Imput string is not proper json.")
        LOG.error(e)
        context.abort()

    if not isinstance(json_list, list):
        LOG.error("Cannot read input. Its not list of jsons.")
        context.abort()

    LOG.info("json is read.")
    load_aplication_tags(adapter, json_list)
