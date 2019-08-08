import logging
import copy
import collections

from datetime import datetime as dt
import vogue.models.case_analysis as analysis_model

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


def update_mongo_doc_sample(mongo_doc: dict, analysis_dict: dict,
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

    if analysis_case in mongo_doc[
            'case_names'] and analysis_workflow in mongo_doc['cases'][
                analysis_case]['workflows']:
        # 1.a. case exists and workflow exists
        mongo_doc['cases'][analysis_case][analysis_workflow].extend(
            new_analysis['cases'][analysis_case][analysis_workflow])
    elif analysis_case in mongo_doc[
            'case_names'] and analysis_workflow not in mongo_doc['cases'][
                analysis_case]['workflows']:
        # 1.b case exists but workflow doesn't
        mongo_doc['cases'][analysis_case]['workflows'].append(
            analysis_workflow)
        mongo_doc['cases'][analysis_case][analysis_workflow] = new_analysis[
            'cases'][analysis_case][analysis_workflow]
    else:
        # 2. case doesn't exists, and naturally there won't be any workflows
        mongo_doc['cases'][analysis_case] = recursive_default_dict()
        mongo_doc['cases'][analysis_case]['workflows'] = new_analysis['cases'][
            analysis_case]['workflows']
        mongo_doc['cases'][analysis_case][analysis_workflow] = new_analysis[
            'cases'][analysis_case][analysis_workflow]
        mongo_doc['case_names'].append(analysis_case)
        mongo_doc = convert_defaultdict_to_regular_dict(mongo_doc)

    return mongo_doc


def build_single_case(analysis_dict: dict, case_analysis_type: str):
    '''
    Prepare a case analysis dictionary
    '''
    case_analysis = recursive_default_dict()
    case_analysis[case_analysis_type] = copy.deepcopy(analysis_dict[case_analysis_type])
    case_analysis = convert_defaultdict_to_regular_dict(case_analysis)

    return case_analysis


def build_mongo_case(analysis_dict: dict, case_analysis: dict):
    '''
    Build a mongo case docuemtn dictionary
    '''
    analysis_case = analysis_dict['case']
    analysis_workflow = analysis_dict['workflow']
    workflow_version = analysis_dict['workflow_version']
    analysis_samples = list(analysis_dict['sample'])

    analysis = recursive_default_dict()

    analysis[analysis_workflow] = list()
    analysis['workflows'] = list()
    analysis['samples'] = list()

    workflow_data = {
        **case_analysis,
        **{
            'workflow_version': workflow_version,
            'added': dt.today()
        }
    }
    analysis[analysis_workflow].append(workflow_data)
    analysis['workflows'].append(analysis_workflow)
    analysis['samples'].extend(analysis_samples)

    analysis = convert_defaultdict_to_regular_dict(analysis)

    return analysis


def update_mongo_doc_case(mongo_doc: dict, analysis_dict: dict,
                          new_analysis: dict):
    '''
    '''

    analysis_samples = analysis_dict['sample']
    analysis_case = analysis_dict['case']
    analysis_workflow = analysis_dict['workflow']
    workflow_version = analysis_dict['workflow_version']

    if analysis_workflow in mongo_doc['workflows']:
        # 1.a. case exists and workflow exists
        mongo_doc[analysis_workflow].extend(new_analysis[analysis_workflow])
    else:
        # 1.b case exists but workflow doesn't
        mongo_doc['workflows'].append(analysis_workflow)
        mongo_doc[analysis_workflow] = new_analysis[analysis_workflow]

    for sample in analysis_samples:
        if sample not in mongo_doc['samples']:
            LOG.info("A new sample %s is added to the case %s", sample,
                     analysis_case)
            mongo_doc['samples'].append(sample)

    return mongo_doc


def build_analysis(analysis_dict: dict, analysis_type: str,
                   valid_analysis: list, current_analysis: dict,
                   case_analysis_type: str, build_case: bool):
    '''
    Builds analysis dictionary based on input analysis_dict and prepares a mongo_doc.
    '''

    if build_case:
        case_analysis = build_single_case(analysis_dict=analysis_dict, case_analysis_type=case_analysis_type)
        analysis = build_mongo_case(analysis_dict=analysis_dict,
                                    case_analysis=case_analysis)
    else:
        sample_analysis = build_single_sample(analysis_dict=analysis_dict,
                                              analysis_type=analysis_type,
                                              valid_analysis=valid_analysis)
        analysis = build_mongo_sample(analysis_dict=analysis_dict,
                                      sample_analysis=sample_analysis)

    sample_id = analysis_dict['sample']
    analysis_case = analysis_dict['case']
    analysis_workflow = analysis_dict['workflow']
    workflow_version = analysis_dict['workflow_version']

    if current_analysis is None:
        # if there is no current analysis, return the built analysis
        mongo_doc = copy.deepcopy(analysis)
        if build_case:
            mongo_doc['_id'] = analysis_case
        else:
            mongo_doc['_id'] = sample_id

    else:
        # if there is a current analysis, pop added and updated keys
        # and continue building the rest of the mongo sample
        mongo_doc = copy.deepcopy(current_analysis)
        mongo_doc.pop('added')
        if 'updated' in mongo_doc.keys():
            mongo_doc.pop('updated')

        if build_case:
            mongo_doc = update_mongo_doc_case(mongo_doc=mongo_doc,
                                              analysis_dict=analysis_dict,
                                              new_analysis=analysis)
        else:
            mongo_doc = update_mongo_doc_sample(mongo_doc=mongo_doc,
                                                analysis_dict=analysis_dict,
                                                new_analysis=analysis)

    return mongo_doc
