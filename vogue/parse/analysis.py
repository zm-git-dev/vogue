import logging
import copy

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
