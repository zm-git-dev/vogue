from vogue.build.index_category import build_index_category
import logging
LOG = logging.getLogger(__name__)

def load_all(adapter, lims):
    """Function to load indexes from a step into the database"""

    LOG.info('Fetching all reagent types from lims...')
    lims_indexes = lims.get_reagent_types()

    LOG.info('Loading reagent types into the index_cathegory colleciton.')
    for lims_index in lims_indexes:
        mongo_index = build_index_category(lims_index)
        adapter.add_or_update_index_category(mongo_index)
