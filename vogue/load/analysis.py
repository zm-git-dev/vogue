from vogue.adapter import VougeAdapter
from vogue.build.analysis import build_analysis

def load_cancer_analysis(adapter: VougeAdapter, lims_id=None, dry_run=False, analysis : dict={}):
    """Load information from a cancer analysis"""
    
    sample_obj = adapter.sample(lims_id)
    if not sample_obj:
        raise SyntaxError("Sample {} does not exist".format(lims_id))
    
    ## TODO build the analysis object
    analysis_obj = build_analysis(analysis, 'QC' )
    ## TODO load the object with adapter
    adapter.load_analysis(analysis_obj)
    
    return analysis_obj
