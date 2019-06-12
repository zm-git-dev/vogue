
from vogue.parse.build.sample_analysis import *


def build_samples(case: dict)-> dict:
    """Build samples for the sample_analysis collection 
    from one case in the case_analysis collection"""
    
    mip_analysis = Mip(case)
    mongo_samples = []

    for sample_id in case.get('samples'):
        mongo_sample = {'_id' : sample_id}
        mongo_sample['mip'] = mip_analysis.build_mip_sample(sample_id)

        for key in list(mongo_sample.keys()):
            stuff_we_dont_want = [None, [], {}]
            if mongo_sample[key] in stuff_we_dont_want:
                mongo_sample.pop(key)
        mongo_samples.append(mongo_sample)

    return mongo_samples