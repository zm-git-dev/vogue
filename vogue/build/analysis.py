import logging
LOG = logging.getLogger(__name__)


def validate_conf(analysis_conf):
    """
    Takes input analysis_conf dictionary and validates entries.

    Checks for there are at least two keys in analysis_conf dictionary. If there is less than two, or the key doesn't
    exist, disqualifies the file and returns False
    """
    try:
        if len(analysis_conf['report_saved_raw_data'].keys()) > 1:
            LOG.info('Input multiqc file is probably properly formatted.')
            valid_dict = True
        else:
            LOG.warning(
                'Input multiqc file has too few keys in it OR it is truncated.'
            )
            valid_dict = False
    except (KeyError, AttributeError) as e:
        LOG.warning(
            'Input multiqc file is either not a multiqc report or it it is truncated.'
        )
        valid_dict = False

    return valid_dict


def build_analysis(analysis: dict, analysis_type: str):
    """build a analysis object"""
    return analysis
