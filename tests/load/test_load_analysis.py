from vogue.load.analysis import load_cancer_analysis
from vogue.tools.cli_utils import json_read

VALID_JSON = 'tests/fixtures/valid_multiqc.json'


def test_load_simple_cancer(adapter, test_sample, cancer_analysis):
    """docstring for test_load_simple_cancer"""
    ## GIVEN a adapter with a sample

    assert adapter.sample_collection.insert_one(test_sample)

    assert adapter.analysis_collection.find_one() is None
    ## WHEN adding a cancer analysis

    lims_id = test_sample['_id']

    cancer_analysis = json_read(VALID_JSON)
    analysis_obj = load_cancer_analysis(adapter, lims_id, False,
                                        cancer_analysis)

    ## THEN assert the analysis was added
    assert adapter.analysis_collection.find_one()
