import sys
import logging
from vogue.build.status_db import build_application_tag
LOG = logging.getLogger(__name__)
   

def load_aplication_tags(adapter, db_json_list, dry_run=False):
    
    
    if dry_run:
        LOG.info("Will go through all application tags in status-db and add/update them in status-db.")
        return

    for application_tag in db_json_list:
        mongo_application_tag = build_application_tag(application_tag)
        adapter.add_or_update_application_tag(mongo_application_tag)
