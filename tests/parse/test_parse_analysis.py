from vogue.parse.analysis import validate_conf
from vogue.models.analysis import ANALYSIS_SETS
from vogue.tools.cli_utils import json_read

VALID_JSON = 'tests/fixtures/valid_multiqc.json'

def test_validate_conf():

    ## GIVEN a valid json file with some valid analysis keys
    ## 1. read json file json_read
    ## 2. validate input dict vid the analysis set models

    analysis_conf = json_read(VALID_JSON)

    ## WHEN extracting the valid keys from the json, using validate_conf
    mongo_sample_analysis = validate_conf(analysis_conf = analysis_conf)

    ## THEN the putput should be a list and not a empty list
    assert isinstance(mongo_sample_analysis, list)
   