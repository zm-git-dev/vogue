from vogue.parse.load.bioinfo_analysis import inspect_analysis_result
from vogue.models.bioinfo_analysis import ANALYSIS_SETS
from vogue.tools.cli_utils import yaml_read

VALID_JSON = 'tests/fixtures/valid_multiqc.yaml'


def test_inspect_bioinfo_result():

    # GIVEN a valid json file with some valid analysis keys
    # 1. read json file json_read
    # 2. validate input dict vid the analysis set models

    analysis_conf = dict()
    analysis_conf['case_analysis_type'] = 'multiqc'
    analysis_conf['multiqc'] = yaml_read(VALID_JSON)

    # WHEN extracting the valid keys from the json, using validate_conf
    valid_key_list = inspect_analysis_result(analysis_dict=analysis_conf)

    # THEN the output should be a list
    assert isinstance(valid_key_list, list)
