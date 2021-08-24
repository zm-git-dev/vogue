import sys
import logging
from vogue.build.application_tag import build_application_tag
from vogue.exceptions import MissingApplicationTag

LOG = logging.getLogger(__name__)


def load_aplication_tags(adapter, json_list):
    """Will go through all application tags in json_list and add/update them to trending-db.

    Args:
        adapter(adapter.VogueAdapter)
        json_list(list(dict)): [{'tag':'MELPCFR030', 'category':'wgs',...},...]
    """

    for application_tag in json_list:
        try:
            mongo_application_tag = build_application_tag(application_tag)
            adapter.add_or_update_document(mongo_application_tag, adapter.app_tag_collection)
        except MissingApplicationTag:
            LOG.warning("ApplicationTag missing in JSON list")
