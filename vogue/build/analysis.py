import logging
import copy

LOG = logging.getLogger(__name__)

import vogue.models.analysis as analysis_model



def build_analysis(analysis_dict: dict, analysis_type: str, valid_analysis: list, sample_id):
    '''
    Builds analysis dictionary based on input analysis_dict. This function will remove analysis json that are not part
    of the matching model. analysis_type is a single key matching ANALYSIS_SETS's first level keys.
    '''

    # Match valid_analysis with the analysis_type of ANALYSIS_SETS
    analysis_common_keys = [e for e in valid_analysis if e in list(analysis_model.ANALYSIS_SETS[analysis_type].keys())] 

    # A new dictionary is constructed instead of dropping unrelevant keys. Or maybe one could deepcopy analysis_dict and
    # remove the irrelevant keys.
    analysis = dict()
    for common_key in analysis_common_keys:
        analysis[common_key] = analysis_dict[common_key]

    mongo_sample = copy.deepcopy(analysis)
    mongo_sample['_id'] = sample_id

    return mongo_sample

