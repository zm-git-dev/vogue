from genologics.entities import Process
from genologics.lims import Lims

from vogue.parse.flowcell import parse_run_data


def build_run(run: Process)-> dict:
    """Parse lims sample"""
        
    mongo_run = {'_id' : run.udf.get('Run ID')}

    for key, val in run.udf.items():
        mongo_run[key] = val

    avg_run_data = parse_run_data(run)
    for key, val in avg_run_data.items():
        mongo_run[key] = val

    for key in list(mongo_run.keys()):
        if mongo_run[key] is None:
            mongo_run.pop(key)

    return mongo_run