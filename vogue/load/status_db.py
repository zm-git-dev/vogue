import logging
from vogue.build.status_db import build_application_tag
LOG = logging.getLogger(__name__)
   

def load_one_sample(adapter, lims_id=None, lims_sample=None, lims=None, dry_run=False):
    lims_sample = lims_sample or Sample(lims, id = lims_id)
    if not lims_sample:
        LOG.critical("The sample does not exist in the database in the LIMS database.")
        raise SyntaxError()
    mongo_application_tag = build_application_tag(lims_sample, lims)
    
    if dry_run:
        existing_sample = adapter.sample(lims_sample.id)
        if existing_sample:
            LOG.info("The sample exist in the database.")
        else:
            LOG.info("The sample does not exist in the database.")
        LOG.info("Sample informamtion from lims to add/update: \n %s", mongo_application_tag)
        return
    
    adapter.add_or_update_application_tag(mongo_application_tag)
