from genologics.entities import Sample
from genologics.lims import Lims

import logging
from vogue.build.lims import build_sample
LOG = logging.getLogger(__name__)
   

def load_one_sample(adapter, lims_id=None, lims_sample=None, lims=None, dry_run=False):

    lims_sample = lims_sample or Sample(lims, id = lims_id)
    if not lims_sample:
        LOG.critical("The sample does not exist in the database in the LIMS database.")
        raise SyntaxError()

    mongo_sample = build_sample(lims_sample, lims, adapter)

    
    if dry_run:
        existing_sample = adapter.sample(lims_sample.id)
        if existing_sample:
            LOG.info("The sample exist in the database.")
        else:
            LOG.info("The sample does not exist in the database.")
        LOG.info("Sample informamtion from lims to add/update: \n %s", mongo_sample)
        return
    

    adapter.add_or_update_sample(mongo_sample)

def load_all_samples(adapter, lims, dry_run=False, start_sample = None):
    if dry_run:
        LOG.info('Will load all lims samples.')
        return
    for sample in lims.get_samples():
        if not start_sample:
            LOG.info(sample.id)
            load_one_sample(adapter, lims_sample=sample, dry_run=dry_run, lims=lims)
        elif start_sample and start_sample == sample.id:
            start_sample = None

 


        