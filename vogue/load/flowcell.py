from vogue.build.flowcell import build_run
from vogue.constants.lims_constants import MASTER_STEPS_UDFS, INSTRUMENTS
import logging

LOG = logging.getLogger(__name__)

SEQUENCING_STEPS = MASTER_STEPS_UDFS["sequenced"]["steps"]


def load_one(adapter, run):
    """Function to load one lims flowcell into the database"""
    run_id = run.udf.get("Run ID")
    if not run_id:
        LOG.warning("Run ID is missing")
        return
    date, instrument = run_id.split("_")[0:2]
    instrument_name = INSTRUMENTS.get(instrument)
    if not instrument_name:
        LOG.warning("Could not get instrument name")
        return
    mongo_run = build_run(run=run, instrument=instrument_name, date=date)
    adapter.add_or_update_document(mongo_run, adapter.flowcell_collection)


def load_all(adapter, lims):
    """Function to load all lims flowcell into the database"""
    for run in lims.get_processes(type=SEQUENCING_STEPS):
        load_one(adapter, run)


def load_recent(adapter, lims, the_date):
    """Function to load all lims flowcell into the database"""
    for run in lims.get_processes(type=SEQUENCING_STEPS, last_modified=the_date):
        load_one(adapter, run)
