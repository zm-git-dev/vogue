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
    # detect if multiqc analysis_dict is multiqc
    if "report_saved_raw_data" in analysis_dict.keys():
        analysis_dict = analysis_dict["report_saved_raw_data"]

    for common_key in analysis_common_keys:
        analysis[common_key] = analysis_dict[common_key]

    return analysis


def build_processed_case(analysis_dict: dict,
                         analysis_type: str,
                         valid_analysis: list,
                         cleanup=False):
    '''
    Builds an analysis dict from input information provided by user.
    '''

    case_analysis = dict()
    if not cleanup:
        case_analysis = analysis_dict
    elif cleanup and 'all' in analysis_type:
        for my_analysis in analysis_model.ANALYSIS_DESC.keys():
            tmp_analysis_dict = extract_valid_analysis(
                analysis_dict=analysis_dict,
                analysis_type=my_analysis,
                valid_analysis=valid_analysis)
            if tmp_analysis_dict:
                case_analysis = {**case_analysis, **tmp_analysis_dict}
    else:
        case_analysis = extract_valid_analysis(analysis_dict=analysis_dict,
                                               analysis_type=my_analysis,
                                               valid_analysis=valid_analysis)
    return case_analysis


def build_unprocessed_case(analysis_dict: dict):
    '''
    Prepare a case analysis dictionary
    '''
    case_analysis = recursive_default_dict()
    case_analysis_type = analysis_dict['case_analysis_type']
    case_analysis = copy.deepcopy(analysis_dict[case_analysis_type])
    case_analysis = convert_defaultdict_to_regular_dict(case_analysis)

    return case_analysis


def build_mongo_case(analysis_dict: dict, case_analysis: dict, processed=False):
    '''
    Build a mongo case docuemtn dictionary
    '''
    analysis_case = analysis_dict['case']
    analysis_workflow = analysis_dict['workflow']
    case_analysis_type = analysis_dict['case_analysis_type']
    workflow_version = analysis_dict['workflow_version']
    analysis_samples = list(analysis_dict['sample'])

    analysis = recursive_default_dict()

    if not processed:
        analysis[analysis_workflow][case_analysis_type] = list()
    else:
        analysis[case_analysis_type] = list()
    analysis['workflows'] = list()
    analysis['case_analysis_types'] = list()
    analysis['samples'] = list()

    workflow_data = {
        **case_analysis,
        **{
            'workflow_version': workflow_version,
            'added': dt.today()
        }
    }
    if not processed:
        analysis[analysis_workflow][case_analysis_type].append(workflow_data)
    else:
        analysis[case_analysis_type].append(workflow_data[case_analysis_type])
    analysis['case_analysis_types'].append(case_analysis_type)
    analysis['workflows'].append(analysis_workflow)
    analysis['samples'].extend(analysis_samples)

    analysis = convert_defaultdict_to_regular_dict(analysis)

    return analysis


def update_mongo_doc_case(mongo_doc: dict, analysis_dict: dict,
                          new_analysis: dict, processed=False):
    '''
    '''

    analysis_samples = analysis_dict['sample']
    analysis_case = analysis_dict['case']
    case_analysis_type = analysis_dict['case_analysis_type']
    analysis_workflow = analysis_dict['workflow']
    workflow_version = analysis_dict['workflow_version']

    if not processed:
        if analysis_workflow in mongo_doc['workflows'] and case_analysis_type in mongo_doc['case_analysis_types']:
            # 1.a. case exists and workflow exists
            mongo_doc[analysis_workflow][case_analysis_type].extend(new_analysis[analysis_workflow][case_analysis_type])
        elif analysis_workflow in mongo_doc['workflows'] and case_analysis_type not in mongo_doc['case_analysis_types']:
            # 1.b. case exists and workflow exists
            mongo_doc[analysis_workflow][case_analysis_type] = copy.deepcopy(new_analysis[analysis_workflow][case_analysis_type])
            mongo_doc['case_analysis_types'].append(case_analysis_type)
        else:
            # 1.c case exists but workflow doesn't
            mongo_doc['workflows'].append(analysis_workflow)
            mongo_doc[analysis_workflow] = new_analysis[analysis_workflow]
    else:
        if case_analysis_type in mongo_doc['case_analysis_types']:
             # 1.a. case exists and workflow exists
             mongo_doc[case_analysis_type].extend(new_analysis[case_analysis_type])
        else:
            # 1.b. case exists and workflow exists            
            mongo_doc[case_analysis_type] = copy.deepcopy(new_analysis[case_analysis_type])
            mongo_doc['case_analysis_types'].append(case_analysis_type)

    for sample in analysis_samples:
        if sample not in mongo_doc['samples']:
            LOG.info("A new sample %s is added to the case %s", sample,
                     analysis_case)
            mongo_doc['samples'].append(sample)

    return mongo_doc


def build_analysis(analysis_dict: dict,
                   analysis_type: str,
                   valid_analysis: list,
                   current_analysis: dict,
                   process_case=False,
                   cleanup=False):
    '''
    Builds analysis dictionary based on input analysis_dict and prepares a mongo_doc.
    
    If not process_case, then do not validate any keys in the analysis_dict.
    This will only load into bioinfo_raw.

    If process_case, then extract valid keys from analysis_dict.
    '''

    analysis_case = analysis_dict['case']

    if not process_case:
        case_analysis = build_unprocessed_case(analysis_dict=analysis_dict)
    else:
        case_analysis = build_processed_case(analysis_dict=analysis_dict,
                                             analysis_type=analysis_type,
                                             valid_analysis=valid_analysis,
                                             cleanup=cleanup)

    analysis = build_mongo_case(analysis_dict=analysis_dict,
                                processed=process_case,
                                case_analysis=case_analysis)

    if current_analysis is None:
        # if there is no current analysis, return the built analysis
        mongo_doc = copy.deepcopy(analysis)
        mongo_doc['_id'] = analysis_case

    else:
        # if there is a current analysis, pop added and updated keys
        # and continue building the rest of the mongo sample
        mongo_doc = copy.deepcopy(current_analysis)
        mongo_doc.pop('added')
        if 'updated' in mongo_doc.keys():
            mongo_doc.pop('updated')

        mongo_doc = update_mongo_doc_case(mongo_doc=mongo_doc,
                                          analysis_dict=analysis_dict,
                                          new_analysis=analysis,
                                          processed=process_case)

    return mongo_doc
