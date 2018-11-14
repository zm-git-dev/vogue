from vogue.adapter import VogueAdapter
from vogue.build.analysis import build_analysis

def load_cancer_analysis(adapter: VogueAdapter, sample_id: str, analysis: dict):
    """Load information from a cancer analysis"""
    sample_obj = adapter.sample(sample_id)
    if not sample_obj:
        raise SyntaxError("Sample {} does not exist".format(sample_id))
    
    ## TODO build the analysis object
    analysis_obj = build_analysis(analysis, 'cancer')
    ## TODO load the object with adapter
    adapter.load_analysis(analysis_obj)
    
    return analysis_obj