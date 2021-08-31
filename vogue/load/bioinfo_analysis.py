import logging

LOG = logging.getLogger(__name__)


def load_analysis(adapter, lims_id, analysis, processed=False, is_sample=False, dry_run=False):
    """Load information for a bioinfo analysis"""

    if dry_run:
        existing_analysis = adapter.sample(lims_id)
        if existing_analysis:
            LOG.info("The sample exists in the database")
        else:
            LOG.info("The sample does not exist in the database")

        LOG.info("Analysis information for sample %s to add/update: \n %s", lims_id, analysis)
        return

    if not processed and not is_sample:
        adapter.add_or_update_bioinfo_raw(analysis)
        load_status = True
    elif processed and not is_sample:
        adapter.add_or_update_bioinfo_processed(analysis)
        load_status = True
    elif processed and is_sample:
        adapter.add_or_update_bioinfo_samples(analysis)
        load_status = True
    else:
        LOG.warning("No analysis was loaded into database")
        load_status = False

    return load_status
