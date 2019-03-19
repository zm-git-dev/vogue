from vogue.build.flowcell import build_run
from vogue.constants.constants import RUN_TYPES


def load_one(adapter, run):
    """Function to load one lims flowcell into the database"""
    mongo_run = build_run(run=run)
    if mongo_run.get('_id'):
        print('hej')
        #adapter.add_or_update_run(mongo_run)


def load_all(adapter, lims):
    """Function to load all lims flowcell into the database"""
    for run in lims.get_processes(type=RUN_TYPES):
        load_one(adapter, run)
      


