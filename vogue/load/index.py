from vogue.build.index import build_index
from vogue.constants.lims_constants import MASTER_STEPS_UDFS, INSTRUMENTS
import logging
LOG = logging.getLogger(__name__)

REAGENT_LABEL_STEPS = MASTER_STEPS_UDFS['reagent_labels']

def load_one(adapter, step):
    """Function to load indexes from a step into the database"""
    LOG.info('Processing indexes from step: %s' % step.id)
    mongo_indexes = build_index(step)
    for index, mongo_index in mongo_indexes.items():
        adapter.add_or_update_index(mongo_index)


def load_all(adapter, lims):
    """Function to load indexes from all lims flowcells into the database"""
    processes = lims.get_processes(type=REAGENT_LABEL_STEPS)
    LOG.info('Loading data from %s processes' % str(len(processes)))
    for step in processes:
        load_one(adapter, step)

def load_recent(adapter, lims, the_date):
    """Function to load indexes from all lims flowcells run after the_date into the database"""
    processes = lims.get_processes(type=REAGENT_LABEL_STEPS, last_modified=the_date)
    LOG.info('Loading data from %s processes' % str(len(processes)))
    for step in processes:
        load_one(adapter, step)
