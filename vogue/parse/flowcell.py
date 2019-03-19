from vogue.constants.constants import LANE_UDFS
import numpy as np


def parse_run_data(run):
    run_data = {}

    for lane in run.all_outputs():
        for udf in LANE_UDFS:
            value = lane.udf.get(udf)
            print(type(value))
            if not run_data.get(udf):
                run_data[udf] = []
            if isinstance(value, int) or isinstance(value, float):
                run_data[udf].append(value)
    for udf, values in run_data.items():
        run_data[udf]= np.mean(values)

    return run_data    

