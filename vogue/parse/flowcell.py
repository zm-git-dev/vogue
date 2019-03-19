from vogue.constants.constants import LANE_UDFS
import numpy as np


def run_data(run):
    lane_data = {}
    avg_data = {}

    for lane in run.all_outputs():
        name=lane.name
        if not 'Lane' in name.split():
            continue

        lane_data[name] ={}
        for udf in LANE_UDFS:
            value = lane.udf.get(udf)
            lane_data[name][udf] = value
            if not avg_data.get(udf):
                avg_data[udf] = []
            if isinstance(value, int) or isinstance(value, float):
                avg_data[udf].append(value)

    for udf, values in avg_data.items():
        avg_data[udf]= round(np.mean(values),2)

    return lane_data, avg_data 