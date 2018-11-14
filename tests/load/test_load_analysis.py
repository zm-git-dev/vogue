
from vogue.load.analysis import load_cancer_analysis

def test_load_simple_cancer(adapter, test_sample, cancer_analysis):
    """docstring for test_load_simple_cancer"""
    ## GIVEN a adapter with a sample
    
    assert adapter.sample_collection.insert_one(test_sample)

    assert adapter.analysis_collection.find_one() is None
    ## WHEN adding a cancer analysis
    
    sample_id = test_sample['_id']
    analysis_obj = load_cancer_analysis(adapter, sample_id, cancer_analysis)
    print(analysis_obj)
    
    ## THEN assert the analysis was added
    assert adapter.analysis_collection.find_one()