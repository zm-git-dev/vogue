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
    print(analysis_names)

    # Now we need to know which analysis tools or bioinformatic tools in <analysis_conf>'s first level keys are among
    # valid analysis_names above. If indices needed, change i,e and extract i.
    print(list(analysis_conf.keys()))
    valid_analysis = [e for e in list(analysis_conf.keys()) if e in analysis_names]
    print(valid_analysis)

    if not valid_analysis:
        return None

    LOG.info(f'The following keys were found in the input config: {valid_analysis}') 
    return valid_analysis

def build_analysis(multiqc_dict: dict, analysis_type: str):
    """build a analysis object"""

    if not analysis_type in analysis_model.ANALYSIS_SETS.keys():
        LOG.warning(
            f'Analysis did not match the analysis type: {analysis_type}')
        return None

    analysis = dict()

    # Find common analysis between predefined set and config file loaded.
    analysis_common_keys = set(
        analysis_model.ANALYSIS_SETS[analysis_type].keys()) & set(
            multiqc_dict['report_saved_raw_data'].keys())

    for common_key in analysis_common_keys:
        analysis[common_key] = multiqc_dict['report_saved_raw_data'][common_key]

    return analysis
