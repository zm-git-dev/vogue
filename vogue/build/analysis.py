import logging
LOG = logging.getLogger(__name__)

import vogue.models.analysis as analysis_model


def validate_conf(analysis_conf: dict):
    """
    Takes input analysis_conf dictionary and validates entries.

    Checks for there are at least two keys in analysis_conf dictionary. If there is less than two, or the key doesn't
    exist, disqualifies the file and returns False
    """

    # Second level keys in ANALYSIS_SETS are bioinformatic tool name OR analysis name.
    # This line will extract all the second level keys.
    analysis_names = [e for key in analysis_model.ANALYSIS_SETS if isinstance(analysis_model.ANALYSIS_SETS[key], dict)
            for e in analysis_model.ANALYSIS_SETS[key].keys()]

    # Now we need to know which analysis tools or bioinformatic tools in <analysis_conf>'s first level keys are among
    # valid analysis_names above. If indices needed, change i,e and extract i.
    valid_analysis = [e for e in list(analysis_conf.keys()) if e in analysis_names]

    if not valid_analysis:
        return None

    LOG.info(f'The following keys were found in the input config: {valid_analysis}') 
    return valid_analysis

def build_analysis(analysis_dict: dict, analysis_type: str, valid_analysis: str):
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

    return analysis
