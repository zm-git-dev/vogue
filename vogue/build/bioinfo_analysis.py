import logging
import copy
import collections

from datetime import datetime as dt
import vogue.models.bioinfo_analysis as analysis_model
from vogue.tools.cli_utils import recursive_default_dict
from vogue.tools.cli_utils import convert_defaultdict_to_regular_dict

LOG = logging.getLogger(__name__)


def get_common_keys(valid_analysis: list, analysis_type: str):
    '''
    Match a list of values with keys from a MODEL dictionary

    input: valid_analysis as list
    output: analysis_common_keys as list
    '''

    # Match valid_analysis with the analysis_type of ANALYSIS_SETS
    analysis_common_keys = list()
    for my_analysis in valid_analysis:
        if my_analysis in list(
                analysis_model.ANALYSIS_SETS[analysis_type].keys()):
            analysis_common_keys.append(my_analysis)

    return analysis_common_keys


def extract_valid_analysis(analysis_dict: dict, analysis_type: str,
                           valid_analysis: list):
    '''
    Extracts analysis dictionary based on input analysis_dict. This function will remove analysis json that are not part
    of the matching model. analysis_type is a single key matching ANALYSIS_SETS's first level keys.

    Input:
        analysis_dict: A dictionary of bioinfo analysis stats.
        analysis_type: A string of analysis type. This is provided by user.
        valid_analysis: A list of analysis to be extracted from analysis dict.
    Output:
        analysis: A dictionary of valid_analysis as keys extracted from analysis_dict
    '''

    case_analysis_type = analysis_dict['case_analysis_type']

    analysis_common_keys = get_common_keys(valid_analysis, analysis_type)

    # A new dictionary is constructed instead of dropping unrelevant keys. Or maybe one could deepcopy analysis_dict and
    # remove the irrelevant keys.
    analysis = dict()

    for common_key in analysis_common_keys:
        # detect if multiqc analysis_dict is multiqc
        if case_analysis_type == "multiqc":
            analysis[common_key] = analysis_dict["multiqc"][
                "report_saved_raw_data"][common_key]
        elif case_analysis_type == "microsalt":
            analysis[common_key] = analysis_dict["microsalt"][common_key]

    return analysis


def build_processed_case(analysis_dict: dict,
                         analysis_type: str,
                         valid_analysis: list,
                         cleanup=False):
    '''
    Builds an analysis dict from input information provided by user.

    Input:
        analysis_dict: A dictionary of bioinfo stats to be prepared for bioinfo_processed collection
        analysis_type: A string for analysis_type to be extracted from from analysis_dict
        valid_analysis: A list of valid analysis to found within analysis_dict
        cleanup: Flag to cleanup unwanted keys from analysis_dict using info from valid_analysis and analysis_type
    Output:
        case_analysis: A dictionary with information about workflow and case_analysis_type(e.g. multiqc),
            workflow version, and date added.
    '''

    case_analysis = copy.deepcopy(analysis_dict)
    case_analysis_type = analysis_dict['case_analysis_type']
    analysis_workflow = analysis_dict['workflow']
    workflow_version = analysis_dict['workflow_version']
    case_analysis[analysis_workflow] = dict()
    case_analysis[analysis_workflow][case_analysis_type] = dict()
    if not cleanup:
        case_analysis[analysis_workflow][case_analysis_type] = analysis_dict[
            case_analysis_type]
    else:
        for my_analysis in analysis_model.ANALYSIS_DESC.keys():
            tmp_analysis_dict = extract_valid_analysis(
                analysis_dict=analysis_dict,
                analysis_type=my_analysis,
                valid_analysis=valid_analysis)
            if tmp_analysis_dict:
                case_analysis[analysis_workflow][case_analysis_type] = {
                    **case_analysis[analysis_workflow][case_analysis_type],
                    **tmp_analysis_dict
                }

    case_analysis[analysis_workflow][case_analysis_type] = {
        **case_analysis[analysis_workflow][case_analysis_type],
        **{
            'workflow_version': workflow_version,
            'added': dt.today()
        }
    }

    ## TODO: add the following to control over which valid analysis to load.
    ## Example:
    ##    elif cleanup and 'all' in analysis_type:
    ##    else:
    ##        case_analysis = extract_valid_analysis(analysis_dict=analysis_dict,
    ##                                               analysis_type=my_analysis,
    ##                                               valid_analysis=valid_analysis)

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


def build_mongo_case(analysis_dict: dict, case_analysis: dict,
                     processed=False):
    '''
    Build a mongo case document dictionary
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
        analysis[analysis_workflow][case_analysis_type] = dict()

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
        analysis[analysis_workflow][case_analysis_type] = workflow_data[
            analysis_workflow][case_analysis_type]
        #analysis[analysis_workflow] = {**analysis[analysis_workflow], **workflow_data[analysis_workflow][case_analysis_type]}

    analysis['case_analysis_types'].append(case_analysis_type)
    analysis['workflows'].append(analysis_workflow)
    analysis['samples'].extend(analysis_samples)

    analysis = convert_defaultdict_to_regular_dict(analysis)

    return analysis


def update_mongo_doc_case(mongo_doc: dict, analysis_dict: dict,
                          new_analysis: dict):
    '''
    Args:
        mongo_doc: an existing analysis retrieved from MongoDB 
        analysis_dict: a dictionary parsed from CLI
        new_analysis: new analysis dictionary to be loaded to MongoDB

    Returns:
        mongo_doc: an updated mongo_doc from Args

    Add or update mongo document for case data
    Adds or updates within processed or raw bioinfo collection
    '''

    analysis_samples = analysis_dict['sample']
    analysis_case = analysis_dict['case']
    analysis_type = analysis_dict['case_analysis_type']
    analysis_workflow_type = analysis_dict['workflow']
    workflow_version = analysis_dict['workflow_version']

    if analysis_workflow_type not in mongo_doc:
        mongo_doc[analysis_workflow_type] = {}

    if analysis_type not in mongo_doc[analysis_workflow_type]:
        mongo_doc[analysis_workflow_type][analysis_type] = new_analysis[
            analysis_workflow_type][analysis_type]
    else:
        mongo_doc[analysis_workflow_type] = {
            **new_analysis[analysis_workflow_type],
            **mongo_doc[analysis_workflow_type]
        }

    if analysis_workflow_type not in mongo_doc['workflows']:
        mongo_doc['workflows'].append(analysis_workflow_type)

    if analysis_type not in mongo_doc['case_analysis_types']:
        LOG.info("A new analysis type %s is added to the case %s",
                 analysis_type, analysis_case)
        mongo_doc['case_analysis_types'].append(analysis_type)

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
                                          new_analysis=analysis)

    return mongo_doc


def build_bioinfo_sample(analysis_dict: dict,
                         sample_id: str,
                         process_case=False):
    '''
    Builds sample analysis from analysis_dict

    analysis_dict is a processed dictionary, i.e. from bioinfo_processed
    '''

    analysis_case = analysis_dict['_id']
    analysis_workflows = analysis_dict['workflows']
    case_analysis_types = analysis_dict['case_analysis_types']

    if not process_case:
        return None

    mongo_doc = recursive_default_dict()
    mongo_doc['_id'] = sample_id
    mongo_doc['workflows'] = analysis_workflows
    mongo_doc['case_analysis_types'] = case_analysis_types
    for workflow in analysis_workflows:
        for analysis_type in case_analysis_types:
            simple_analysis_dict = analysis_dict[workflow][analysis_type]
            # check if sample_id is in key
            for metric, samples in simple_analysis_dict.items():
                if isinstance(samples, dict):
                    for sample in samples.keys():
                        # split key by underscore
                        if sample_id in sample.split("_"):
                            mongo_doc[workflow][metric] = samples[sample]
                            mongo_doc[workflow]['case'] = analysis_case

    mongo_doc = convert_defaultdict_to_regular_dict(mongo_doc)
    return mongo_doc
