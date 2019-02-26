import logging

from genologics.entities import Sample
from genologics.lims import Lims

from vogue.build.analysis import build_analysis

LOG = logging.getLogger(__name__)

def load_analysis(adapter, lims_id, dry_run=False, analysis : dict={}):
    """Load information from a cancer analysis"""
    
    if dry_run:
        existing_analysis = adapter.sample(lims_id)
        if existing_analysis:
            LOG.info("The sample exists in the database")
        else:
            LOG.info("The sample does not exist in the database")

        LOG.info("Analysis information for sample %s to add/update: \n %s", lims_id, analysis)
        return

    adapter.add_or_update_analysis(analysis)

