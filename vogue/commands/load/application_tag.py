import logging
import click
import json
from flask.cli import with_appcontext, current_app
from vogue.load.application_tag import load_aplication_tags

LOG = logging.getLogger(__name__)


@click.command("apptag", short_help="Reads json with application tag info.")
@click.argument("application-tags")
@with_appcontext
def application_tags(application_tags):
    """Reads json string with application tags. Eg:'[{"tag":"MELPCFR030", "category":"wgs",...},...]'"""

    LOG.info("Reading json.")
    try:
        json_list = json.loads(application_tags)
    except json.JSONDecodeError as e:
        LOG.error("Imput string is not proper json.")
        LOG.error(e)
        raise click.Abort()

    if not isinstance(json_list, list):
        LOG.error("Cannot read input. Its not list of jsons.")
        raise click.Abort()

    LOG.info("json is read.")
    load_aplication_tags(current_app.adapter, json_list)
