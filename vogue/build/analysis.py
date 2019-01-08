import logging
LOG = logging.getLogger(__name__)

import vogue.models.analysis as analysis_model


def validate_conf(analysis_conf: dict):
    """
    Takes input analysis_conf dictionary and validates entries.

    Checks for there are at least two keys in analysis_conf dictionary. If there is less than two, or the key doesn't
    exist, disqualifies the file and returns False
    """

    try:
        if 'report_saved_raw_data' in analysis_conf.keys():
            LOG.info('Input seems to be a valid multiqc report')
            return True
        else:
            LOG.warning('Input does not seem to be a multiqc report')
            return False

    except (KeyError, AttributeError) as e:
        LOG.warning(
            'Input multiqc file is either not a multiqc report or it it is truncated.'
        )
        return False


def build_analysis(multiqc_dict: dict, analysis_type: str):
    """build a analysis object"""

    if analysis_type in analysis_model.ANALYSIS_SETS.keys():

        analysis = dict()

        # Find common analysis between predefined set and config file loaded.
        analysis_sets = set(
            analysis_model.ANALYSIS_SETS[analysis_type].keys()) & set(
                multiqc_dict['report_saved_raw_data'].keys())

        for a in analysis_sets:
            analysis[a] = multiqc_dict['report_saved_raw_data'][a]

        return analysis

    else:
        LOG.warning(
            f'Analysis did not match the analysis type: {analysis_type}')
        return None
