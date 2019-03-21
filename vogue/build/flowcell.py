from genologics.entities import Process
from genologics.lims import Lims

from vogue.parse.flowcell import run_data
import datetime as dt
import math

def filter_none(mongo_dict):
    for key in list(mongo_dict.keys()):
        val = mongo_dict[key]
        if isinstance(val,(dict, str, dt.datetime)):
            continue
        if val is None or math.isnan(val):
            mongo_dict.pop(key)
    return mongo_dict

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
    mongo_run['avg'] = filter_none(avg_data)
    mongo_run['lanes'] = filter_none(lane_data)


    mongo_run = filter_none(mongo_run)

    return mongo_run