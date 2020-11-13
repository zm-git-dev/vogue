from genologics.entities import Process
from genologics.lims import Lims

from vogue.parse.build.flowcell import run_data, filter_none
import datetime as dt


def build_run(run: Process, instrument: str, date: str) -> dict:
    """Build flowcell document from lims data."""

    mongo_run = {
        '_id': run.udf.get('Run ID'),
        'instrument': instrument,
        'date': dt.datetime.strptime(date, '%y%m%d')
    }

    for key, val in run.udf.items():
        if isinstance(val, dt.date):
            val = dt.datetime.strptime(val.isoformat(), '%Y-%m-%d')
        mongo_run[key] = val

    lane_data, avg_data = run_data(run)
    mongo_run['avg'] = avg_data
    mongo_run['lanes'] = lane_data

    mongo_run = filter_none(mongo_run)

    return mongo_run
