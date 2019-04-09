from vogue.build.analysis import build_analysis
from vogue.models.analysis import ANALYSIS_SETS
from vogue.tools.cli_utils import json_read



def test_build_analysis(get_valid_json):

    # GIVEN a analysis dictionary valid_analysis_dict and analysis_type
    # 1. read json file json_read
    # 2. build an analysis mongo sample using build_analysis

    valid_analysis_dict = json_read(get_valid_json)
    analysis_type = 'QC'
    valid_analysis_names = ANALYSIS_SETS[analysis_type].keys()
    sample_id = 'test_sample'

    # WHEN building a mongo analysis document
    mongo_sample_analysis = build_analysis(
        analysis_dict=valid_analysis_dict,
        analysis_type=analysis_type,
        valid_analysis=valid_analysis_names,
        sample_id=sample_id)

    # THEN assert the mongo_sample_analysis has key _id with value sample_id
    assert sample_id == mongo_sample_analysis.pop('_id')
    # THEN assert all keys in mongo_sample_analysis are valid
    assert set(mongo_sample_analysis.keys()).issubset(
        set(valid_analysis_names))


def test_build_analysis_invalid_key(get_valid_json):

    # GIVEN a analysis dictionary invalid valid_analysis_dict and analysis_type
    # 1. read json file json_read
    # 2. build an analysis mongo sample using build_analysis

    valid_analysis_dict = json_read(get_valid_json)
    analysis_type = 'QC'
    valid_analysis_names = ANALYSIS_SETS[analysis_type].keys()
    sample_id = 'test_sample'
    valid_analysis_dict['invalid_key'] = 34

    # WHEN building a mongo analysis document
    mongo_sample_analysis = build_analysis(
        analysis_dict=valid_analysis_dict,
        analysis_type=analysis_type,
        valid_analysis=valid_analysis_names,
        sample_id=sample_id)

    # THEN assert the mongo_sample_analysis doesnt have the invalid_key
    assert 'invalid_key' not in mongo_sample_analysis.keys()
