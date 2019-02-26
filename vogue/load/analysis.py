import logging

from genologics.entities import Sample
from genologics.lims import Lims

from vogue.build.analysis import build_analysis

LOG = logging.getLogger(__name__)

def load_analysis(adapter, dry_run=False, analysis : dict={}):
    """Load information from a cancer analysis"""
    
    if dry_run:
        existing_sample = adapter.sample(lims_sample.id)
        if existing_sample:
            LOG.info("The sample exists in the database")
        else:
            LOG.info("The sample does not exist in the database")

        LOG.info("Sample information from analysis to add/update: \n %s", mongo_sample)
        return

    adapter.add_or_update_analysis(analysis)

