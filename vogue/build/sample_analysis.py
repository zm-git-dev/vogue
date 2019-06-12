
from vogue.parse.build.sample_analysis import *


def build_sample():
    return {}


def build_samples(case)-> dict:
    """Parse sample"""
    
    mip_analysis = Mip(case)

    mongo_samples = []

    for sample_id in case.get('samples'):
        mongo_sample = {'_id' : sample_id}
        mongo_sample['mip'] = mip_analysis.build_mip_sample(sample_id)

        for key in list(mongo_sample.keys()):
            if mongo_sample[key] is None:
                mongo_sample.pop(key)
        mongo_samples.append(mongo_sample)

    return mongo_samples