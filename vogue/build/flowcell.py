from genologics.entities import Process
from genologics.lims import Lims

from vogue.parse.flowcell import run_data
import datetime as dt

def build_run(run: Process, instrument:str, date:str)-> dict:
    """Parse lims sample"""
        
    mongo_run = {'_id' : run.udf.get('Run ID'), 
                'instrument' : instrument, 
                'date': dt.datetime.strptime(date, '%y%m%d')}

    for key, val in run.udf.items():
        if isinstance(val, dt.date):
            val = dt.datetime.strptime(val.isoformat(), '%Y-%m-%d')
        mongo_run[key] = val

    lane_data, avg_data = run_data(run)
    mongo_run['avg'] = avg_data
    mongo_run['lanes'] = lane_data


    for key in list(mongo_run.keys()):
        if mongo_run[key] is None:
            mongo_run.pop(key)

    return mongo_run