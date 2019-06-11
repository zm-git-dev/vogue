from vogue.build.sample_analysis import build_sample, build_samples
import logging
LOG = logging.getLogger(__name__)



def load_one_sample(adapter, sample_id):
    """Function to load one sample into the sample_analysis collection"""
    # undantagsfunction. Usually one will use load_one_case whenwver a new case is added. 
    # And sometimes load_all
    
    mongo_sample = build_sample(sample_id=sample_id)
    adapter.add_or_update_sample_analysis(mongo_sample)


def load_one_case(adapter, case_id):
    """Function to load all samples in one case into the sample_analysis colleciotn"""
    case = adapter.case_analysis(case_id)
    mongo_samples = build_samples(case = case)
    for mongo_sample in mongo_samples:
        adapter.add_or_update_sample_analysis(mongo_sample)


def load_all(adapter):
    """Function to load all samples found in the case_analysis collection"""
    for case in adapter.case_analysis_collection:
        load_one_case(adapter, case = case)
      

