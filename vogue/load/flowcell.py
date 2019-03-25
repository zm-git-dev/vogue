from vogue.build.flowcell import build_run
from vogue.constants.constants import RUN_TYPES, INSTRUMENTS
import logging
LOG = logging.getLogger(__name__)



def load_one(adapter, run):
    """Function to load one lims flowcell into the database"""

    run_id = run.udf.get('Run ID')
    if not run_id:
        return
    date, instrument = run_id.split('_')[0:2]
    instrument_name =  INSTRUMENTS.get(instrument)
    if not instrument_name:
        LOG.warning("Run ID is missing")
        return
    mongo_run = build_run(run=run, instrument = instrument_name, date=date)
    if mongo_run.get('_id'):
        adapter.add_or_update_run(mongo_run)


def load_all(adapter, lims):
    """Function to load all lims flowcell into the database"""
    for run in lims.get_processes(type=RUN_TYPES):
        load_one(adapter, run)
      


