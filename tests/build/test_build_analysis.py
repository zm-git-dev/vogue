from vogue.build.analysis import build_analysis
from vogue.models.analysis import ANALYSIS_SETS
from vogue.tools.cli_utils import json_read

INVALID_JSON = 'tests/fixtures/not_a_multiqc_report.json'
VALID_JSON = 'tests/fixtures/valid_multiqc.json'
NO_FILE = 'tests/fixtures/no_exist_file.data'
NOT_FILE = 'tests/fixtures'

import pytest


def test_build_analysis():

    # GIVEN a analysis dictionary valid_analysis_dict and analysis_type
    ## 1. read json file json_read
    ## 2. build an analysis mongo sample using build_analysis

    valid_analysis_dict = json_read(VALID_JSON)
    analysis_type = 'QC'
    valid_analysis_names = ANALYSIS_SETS[analysis_type].keys()
    sample_id = 'test_sample'

    ## WHEN building a mongo analysis document
    mongo_sample_analysis = build_analysis(
        analysis_dict=valid_analysis_dict,
        analysis_type=analysis_type,
        valid_analysis=valid_analysis_names,
        sample_id=sample_id)

    ## THEN assert the mongo_sample_analysis has key _id with value sample_id
    assert sample_id == mongo_sample_analysis.pop('_id')
    ## THEN assert all keys in mongo_sample_analysis are valid
    assert set(mongo_sample_analysis.keys()).issubset(
        set(valid_analysis_names))


def test_build_analysis_invalid_key():

    # GIVEN a analysis dictionary invalid valid_analysis_dict and analysis_type
    ## 1. read json file json_read
    ## 2. build an analysis mongo sample using build_analysis

    valid_analysis_dict = json_read(VALID_JSON)
    analysis_type = 'QC'
    valid_analysis_names = ANALYSIS_SETS[analysis_type].keys()
    sample_id = 'test_sample'
    valid_analysis_dict['invalid_key'] = 34

    ## WHEN building a mongo analysis document
    mongo_sample_analysis = build_analysis(
        analysis_dict=valid_analysis_dict,
        analysis_type=analysis_type,
        valid_analysis=valid_analysis_names,
        sample_id=sample_id)

    ## THEN assert the mongo_sample_analysis doesnt have the invalid_key
    assert 'invalid_key' not in mongo_sample_analysis.keys()
