import logging
import copy

import vogue.models.bioinfo_analysis as analysis_model

LOG = logging.getLogger(__name__)


def inspect_analysis_result(analysis_dict: dict):
    """
    Takes input analysis_dict dictionary and validates entries.

    Checks for there are at least two keys in analysis_dict dictionary. If there is less than two, or the key doesn't
    exist, disqualifies the file and returns False
    """

    case_analysis_type = analysis_dict["case_analysis_type"]

    # detect if multiqc analysis_dict is multiqc
    if case_analysis_type == "multiqc":
        analysis_dict = analysis_dict["multiqc"]["report_saved_raw_data"]
    elif case_analysis_type == "microsalt":
        analysis_dict = analysis_dict["microsalt"]
    else:
        LOG.warning("Analysis type %s is not supported for cleanup", case_analysis_type)
        return None

    # Second level keys in ANALYSIS_SETS are bioinformatic tool name OR analysis name.
    # This line will extract all the second level keys.
    analysis_names = [
        e
        for key in analysis_model.ANALYSIS_SETS
        if isinstance(analysis_model.ANALYSIS_SETS[key], dict)
        for e in analysis_model.ANALYSIS_SETS[key].keys()
    ]

    # Now we need to know which analysis tools or bioinformatic tools in <analysis_dict>'s first level keys are among
    # valid analysis_names above. If indices needed, change i,e and extract i.
    valid_analysis = [e for e in list(analysis_dict.keys()) if e in analysis_names]

    if not valid_analysis:
        return None

    LOG.info(f"The following keys were found in the input config: {valid_analysis}")
    return valid_analysis
