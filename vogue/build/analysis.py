import logging
LOG = logging.getLogger(__name__)

import vogue.models.analysis as analysis_model


def validate_conf(analysis_conf: dict):
    """
    Takes input analysis_conf dictionary and validates entries.

    Checks for there are at least two keys in analysis_conf dictionary. If there is less than two, or the key doesn't
    exist, disqualifies the file and returns False
    """

    if not 'report_saved_raw_data' in analysis_conf.keys():
        LOG.warning('Input does not seem to be a multiqc report')
        return False

    LOG.info('Input seems to be a valid multiqc report')
    return True

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
