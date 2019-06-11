
from vogue.parse.build.sample_analysis import *


def build_sample():
    return {}


def build_samples(adapter, case)-> dict:
    """Parse sample"""
    mongo_samples = []
    for sample_id in case.samples:
        mongo_sample = {'_id' : sample_id}
        mongo_sample['insert_size'] = get_insert_size(case, sample_id)

        for key in list(mongo_sample.keys()):
            if mongo_sample[key] is None:
                mongo_sample.pop(key)
        mongo_samples.append(mongo_sample)

    return mongo_samples