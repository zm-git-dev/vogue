



def get_latest_analysis(case, analysis_type):
    all_analysis = case.get(analysis_type)
    if all_analysis:
        latest_analysis = all_analysis[0]
        for analysis in all_analysis:
            if analysis.get('added') > latest_analysis.get('added'):
                latest_analysis = analysis
        return latest_analysis
    return {}

def reduce_keys(dict_long_keys):
    new_dict = {key.split('_')[0]: val for key, val in dict_long_keys.items()}
    return new_dict


class Mip():
    def __init__(self, case):
        self.case = case
        self.mip_analysis = get_latest_analysis(case, 'mip')
        self.added = None
        self.report_saved_raw_data = {}
        self.multiqc_picard_insertSize = {}
        self.multiqc_picard_HsMetrics = {}
        self._set_init()

    def _set_init(self):
        if self.mip_analysis:
            self.added = self.mip_analysis.get('added')
            self.report_saved_raw_data = self.mip_analysis['multiqc']['report_saved_raw_data']
            self.multiqc_picard_insertSize = reduce_keys(self.report_saved_raw_data['multiqc_picard_insertSize'])
            self.multiqc_picard_HsMetrics = reduce_keys(self.report_saved_raw_data['multiqc_picard_HsMetrics'])

    def build_mip_sample(self, sample_id):
        return {'multiqc_picard_insertSize': self.multiqc_picard_insertSize.get(sample_id),
                'multiqc_picard_HsMetrics' : self.multiqc_picard_HsMetrics.get(sample_id),
                'added' : self.added,
                'case' : self.case['_id']}