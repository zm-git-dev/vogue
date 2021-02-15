def get_latest_analysis(case, analysis_type):
    """Get the latest analysis of anaöysis_type from one case"""

    all_analysis = case.get(analysis_type)
    if all_analysis:
        latest_analysis = all_analysis[0]
        for analysis in all_analysis:
            # analysis allways contains the key 'added'
            if analysis.get('added') > latest_analysis.get('added'):
                latest_analysis = analysis
        return latest_analysis
    return {}


def reduce_keys(dict_long_keys):
    """Cut keys generated in the multiqc report. 
    First entry is allways lims sample ID"""

    new_dict = {key.split('_')[0]: val for key, val in dict_long_keys.items()}
    return new_dict


class uSalt():
    """Class to prepare uSalt case_analysis results 
    for uSalt results in the sample_analysis collection"""

    def __init__(self, project):
        self.project = project
        self.uSalt_analysis = get_latest_analysis(project, 'microsalt')
        self.added = None
        self._set_init()

    def _set_init(self):
        if self.uSalt_analysis:
            self.added = self.uSalt_analysis.get('added')
            self.results = self.uSalt_analysis.get('results', {})

    def build_uSalt_sample(self, sample_id):
        """Bulding the uSalt analysis for one sample. 
        Returns {} if the date 'added' is empty."""

        if not self.added:
            return {}

        return {
            'results': self.results.get(sample_id),
            'added': self.added,
            'project': self.project['_id']
        }


class Mip_dna():
    """Class to prepare mip case_analysis results 
    for mip_dna results in the sample_analysis collection"""

    def __init__(self, case):
        self.case = case
        self.mip_dna_analysis = get_latest_analysis(case, 'mip-dna')
        self.added = None
        self.report_saved_raw_data = {}
        self.multiqc_picard_insertSize = {}
        self.multiqc_picard_HsMetrics = {}
        self._set_init()

    def _set_init(self):
        if self.mip_dna_analysis:
            self.added = self.mip_dna_analysis.get('added')
            self.report_saved_raw_data = self.mip_dna_analysis['multiqc'][
                'report_saved_raw_data']
            self.multiqc_picard_insertSize = reduce_keys(
                self.report_saved_raw_data['multiqc_picard_insertSize'])
            self.multiqc_picard_HsMetrics = reduce_keys(
                self.report_saved_raw_data['multiqc_picard_HsMetrics'])

    def build_mip_dna_sample(self, sample_id):
        """Bulding the mip analysis for one sample. 
        Returns {} if the date 'added' is empty."""

        if not self.added:
            return {}

        return {
            'multiqc_picard_insertSize':
            self.multiqc_picard_insertSize.get(sample_id),
            'multiqc_picard_HsMetrics':
            self.multiqc_picard_HsMetrics.get(sample_id),
            'added':
            self.added,
            'case':
            self.case['_id']
        }
