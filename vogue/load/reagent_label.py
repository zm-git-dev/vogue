from vogue.build.reagent_label import build_reagent_label
from vogue.constants.lims_constants import MASTER_STEPS_UDFS, INSTRUMENTS
import logging

LOG = logging.getLogger(__name__)

REAGENT_LABEL_STEPS = MASTER_STEPS_UDFS["reagent_labels"]["steps"]["bcl"]


def load_one(adapter, step):
    """Function to load reagent_labels from a step into the database"""
    LOG.info("Processing reagent_labels from step: %s" % step.id)
    mongo_reagent_labels = build_reagent_label(step)
    for reagent_label, mongo_reagent_label in mongo_reagent_labels.items():
        adapter.add_or_update_document(mongo_reagent_label, adapter.reagent_label_collection)


def load_all(adapter, lims):
    """Function to load reagent_labels from all lims flowcells into the database"""
    processes = lims.get_processes(type=REAGENT_LABEL_STEPS)
    LOG.info("Loading data from %s processes" % str(len(processes)))
    for step in processes:
        load_one(adapter, step)


def load_recent(adapter, lims, the_date):
    """Function to load reagent_labels from all lims flowcells run after the_date into the database"""
    processes = lims.get_processes(type=REAGENT_LABEL_STEPS, last_modified=the_date)
    LOG.info("Loading data from %s processes" % str(len(processes)))
    for step in processes:
        load_one(adapter, step)
