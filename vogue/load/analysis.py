import logging

LOG = logging.getLogger(__name__)


def load_analysis(adapter, lims_id, analysis, is_case, dry_run=False):
    """Load information from a cancer analysis"""

    if dry_run:
        existing_analysis = adapter.sample(lims_id)
        if existing_analysis:
            LOG.info("The sample exists in the database")
        else:
            LOG.info("The sample does not exist in the database")

        LOG.info("Analysis information for sample %s to add/update: \n %s",
                 lims_id, analysis)
        return

    if is_case:
        adapter.add_or_update_analysis_case(analysis)
    else:
        adapter.add_or_update_analysis_sample(analysis)
