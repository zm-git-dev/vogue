from vogue.constants.constants import LANE_UDFS
import numpy as np


def run_data(run):
    lane_data = {}
    avg_data = {}

    for lane in run.all_outputs():
        name=lane.name
        if not 'Lane' in name.split():
            lane = lane.input_artifact_list()[0]
            if not lane.location:
                continue
            name = lane.location[1]

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

    q30_r1 = '% Bases >=Q30 R1'
    q30_r2 = '% Bases >=Q30 R2'
    if q30_r1 in avg_data.keys() and  q30_r2 in avg_data.keys():
        Q30 = np.mean([avg_data[q30_r1],avg_data[q30_r2]])
        avg_data.pop(q30_r1)
        avg_data.pop(q30_r2)
        avg_data['% Bases >=Q30'] = Q30

    return lane_data, avg_data 