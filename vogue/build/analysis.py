import logging
import copy
import collections

LOG = logging.getLogger(__name__)

import vogue.models.analysis as analysis_model

def recursive_default_dict():
    '''
    Recursivly create defaultdict.
    '''
    return collections.defaultdict(recursive_default_dict)

def convert_defaultdict_to_regular_dict(inputdict: dict):
    '''
    Recursively convert defaultdict to dict.
    '''
    if isinstance(inputdict, collections.defaultdict):
        inputdict = {key: convert_defaultdict_to_regular_dict(value) for key, value in inputdict.items()}
    return inputdict

def extract_valid_analysis(analysis_dict: dict, analysis_type: str, valid_analysis: list):
    '''
    Extracts analysis dictionary based on input analysis_dict. This function will remove analysis json that are not part
    of the matching model. analysis_type is a single key matching ANALYSIS_SETS's first level keys.
    '''

    # Match valid_analysis with the analysis_type of ANALYSIS_SETS
    analysis_common_keys = list()
    for my_analysis in valid_analysis:
        if my_analysis in list(analysis_model.ANALYSIS_SETS[analysis_type].keys()):
            analysis_common_keys.append(my_analysis)

    # A new dictionary is constructed instead of dropping unrelevant keys. Or maybe one could deepcopy analysis_dict and
    # remove the irrelevant keys.
    analysis = dict()
    for common_key in analysis_common_keys:
        analysis[common_key] = analysis_dict[common_key]

    return analysis

def build_analysis(analysis_dict: dict, analysis_type: str,
        valid_analysis: list, sample_id: str):

    '''
    Builds analysis dictionary based on input analysis_dict and prepares a mongo_sample.
    '''

    sample_analysis = dict()
    if 'all' in analysis_type:
        for my_analysis in analysis_model.ANALYSIS_DESC.keys():
            tmp_analysis_dict = extract_valid_analysis(analysis_dict=analysis_dict,
                    analysis_type=my_analysis,
                    valid_analysis=valid_analysis)
            if tmp_analysis_dict:
                sample_analysis = {**sample_analysis, **tmp_analysis_dict}
    else:
        sample_analysis = extract_valid_analysis(analysis_dict=analysis_dict, analysis_type=my_analysis, valid_analysis=valid_analysis)


    analysis_case = analysis_dict['case']
    analysis_workflow = analysis_dict['workflow']
    workflow_version = analysis_dict['workflow_version']

    analysis = recursive_default_dict()
    analysis['cases'][analysis_case]['workflows'][analysis_workflow]['workflow_version'] = workflow_version 
    analysis['cases'][analysis_case]['workflows'][analysis_workflow]['analysis'] = sample_analysis
    analysis = convert_defaultdict_to_regular_dict(analysis)

    mongo_sample = copy.deepcopy(analysis)
    mongo_sample['_id'] = sample_id

    return mongo_sample
