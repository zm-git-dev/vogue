import logging
import copy
import collections

from datetime import datetime as dt
import vogue.models.analysis as analysis_model

LOG = logging.getLogger(__name__)


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
        inputdict = {
            key: convert_defaultdict_to_regular_dict(value)
            for key, value in inputdict.items()
        }
    return inputdict


def extract_valid_analysis(analysis_dict: dict, analysis_type: str,
                           valid_analysis: list):
    '''
    Extracts analysis dictionary based on input analysis_dict. This function will remove analysis json that are not part
    of the matching model. analysis_type is a single key matching ANALYSIS_SETS's first level keys.
    '''

    # Match valid_analysis with the analysis_type of ANALYSIS_SETS
    analysis_common_keys = list()
    for my_analysis in valid_analysis:
        if my_analysis in list(
                analysis_model.ANALYSIS_SETS[analysis_type].keys()):
            analysis_common_keys.append(my_analysis)

    # A new dictionary is constructed instead of dropping unrelevant keys. Or maybe one could deepcopy analysis_dict and
    # remove the irrelevant keys.
    analysis = dict()
    for common_key in analysis_common_keys:
        analysis[common_key] = analysis_dict[common_key]

    return analysis


def build_single_sample(analysis_dict: dict, analysis_type: str,
                        valid_analysis: list):
    '''
    Builds an analysis dict from input information provided by user.
    '''

    sample_analysis = dict()
    if 'all' in analysis_type:
        for my_analysis in analysis_model.ANALYSIS_DESC.keys():
            tmp_analysis_dict = extract_valid_analysis(
                analysis_dict=analysis_dict,
                analysis_type=my_analysis,
                valid_analysis=valid_analysis)
            if tmp_analysis_dict:
                sample_analysis = {**sample_analysis, **tmp_analysis_dict}
    else:
        sample_analysis = extract_valid_analysis(analysis_dict=analysis_dict,
                                                 analysis_type=my_analysis,
                                                 valid_analysis=valid_analysis)
    return sample_analysis


def build_mongo_sample(analysis_dict: dict, sample_analysis: dict):
    '''
    Builds a mongo sample from processed analysis dictionary
    '''
    analysis_case = analysis_dict['case']
    analysis_workflow = analysis_dict['workflow']
    workflow_version = analysis_dict['workflow_version']

    analysis = recursive_default_dict()

    analysis['cases'][analysis_case][analysis_workflow] = list()
    analysis['cases'][analysis_case]['workflows'] = list()
    analysis['case_names'] = list()

    workflow_data = {
        **sample_analysis,
        **{
            'workflow_version': workflow_version,
            'added': dt.today()
        }
    }
    analysis['cases'][analysis_case][analysis_workflow].append(workflow_data)
    analysis['cases'][analysis_case]['workflows'].append(analysis_workflow)
    analysis['case_names'].append(analysis_case)

    analysis = convert_defaultdict_to_regular_dict(analysis)

    return analysis


def update_mongo_sample(mongo_sample: dict, analysis_dict: dict,
                        new_analysis: dict):
    '''
    Updates an existing mongo sample dictionary with new analysis dictionary
    Rational on updating an analysis document 
    1.a. If analysis case exists, and there is workflow result, then append current analysis results to the existing
    workflow.
    1.b. If the workflow doesn't exist, then append the new workflow's name to the 'workflow' keys and add a
    key for the new workflow under the key.
    2. If analysis case doesn't exist, add newly built nested analysis dict under a new casename and workflow key.
    Also update the workflows key under new case name.
    '''

    analysis_case = analysis_dict['case']
    analysis_workflow = analysis_dict['workflow']
    workflow_version = analysis_dict['workflow_version']

    if analysis_case in mongo_sample[
            'case_names'] and analysis_workflow in mongo_sample['cases'][
                analysis_case]['workflows']:
        # 1.a. case exists and workflow exists
        mongo_sample['cases'][analysis_case][analysis_workflow].extend(
            new_analysis['cases'][analysis_case][analysis_workflow])
    elif analysis_case in mongo_sample[
            'case_names'] and analysis_workflow not in mongo_sample['cases'][
                analysis_case]['workflows']:
        # 1.b case exists but workflow doesn't
        mongo_sample['cases'][analysis_case]['workflows'].append(
            analysis_workflow)
        mongo_sample['cases'][analysis_case][analysis_workflow] = new_analysis[
            'cases'][analysis_case][analysis_workflow]
    else:
        # 2. case doesn't exists, and naturally there won't be any workflows
        mongo_sample['cases'][analysis_case] = recursive_default_dict()
        mongo_sample['cases'][analysis_case]['workflows'] = new_analysis[
            'cases'][analysis_case]['workflows']
        mongo_sample['cases'][analysis_case][analysis_workflow] = new_analysis[
            'cases'][analysis_case][analysis_workflow]
        mongo_sample['case_names'].append(analysis_case)
        mongo_sample = convert_defaultdict_to_regular_dict(mongo_sample)

    return mongo_sample


def build_analysis(analysis_dict: dict, analysis_type: str,
                   valid_analysis: list, sample_id: str,
                   current_analysis: dict):
    '''
    Builds analysis dictionary based on input analysis_dict and prepares a mongo_sample.
    '''

    sample_analysis = build_single_sample(analysis_dict=analysis_dict,
                                          analysis_type=analysis_type,
                                          valid_analysis=valid_analysis)

    analysis = build_mongo_sample(analysis_dict=analysis_dict,
                                  sample_analysis=sample_analysis)

    analysis_case = analysis_dict['case']
    analysis_workflow = analysis_dict['workflow']
    workflow_version = analysis_dict['workflow_version']

    if current_analysis is None:
        # if there is no current analysis, return the built analysis
        mongo_sample = copy.deepcopy(analysis)
        mongo_sample['_id'] = sample_id

    else:
        # if there is a current analysis, pop added and updated keys
        # and continue building the rest of the mongo sample
        mongo_sample = copy.deepcopy(current_analysis)
        mongo_sample.pop('added')
        if 'updated' in mongo_sample.keys():
            mongo_sample.pop('updated')

        mongo_sample = update_mongo_sample(mongo_sample=mongo_sample,
                                           analysis_dict=analysis_dict,
                                           new_analysis=analysis)

    return mongo_sample
