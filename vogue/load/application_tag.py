import sys
import logging
from vogue.build.application_tag import build_application_tag
from vogue.exceptions import MissingApplicationTag
LOG = logging.getLogger(__name__)
   

def load_aplication_tags(adapter, json_list, dry_run=False):
    """Will go through all application tags in json_list and add/update them to trending-db.
    
    Args:
        adapter(adapter.VogueAdapter)
        json_list(list(dict)): [{'tag':'MELPCFR030', 'category':'wgs',...},...]
        dry_run(bool)
    """
    
    if dry_run:
        LOG.info("Will go through all application tags in json_list and add/update them in trending-db.")
        return

    for application_tag in json_list:
        try:
            mongo_application_tag = build_application_tag(application_tag)
            adapter.add_or_update_application_tag(mongo_application_tag)
        except MissingApplicationTag:
            LOG.warning('ApplicationTag missing in JSON list')
            