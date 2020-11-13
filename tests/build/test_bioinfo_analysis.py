from vogue.build.bioinfo_analysis import get_common_keys


def test_get_common_keys():
    ## GIVEN a list of valid analysis results
    test_valid_analysis = [
        'multiqc_picard_dups', 'new_analysis_type', 'quast_assembly'
    ]
    test_actual_common_keys = ['multiqc_picard_dups']

    ## WHEN extracting the valid ones
    test_common_analysis_keys = get_common_keys(test_valid_analysis, 'multiqc')

    ## THEN return list of the analysis that are valid and exist in the MODELs
    assert all([
        actual_key == common_key for actual_key, common_key in zip(
            test_actual_common_keys, test_common_analysis_keys)
    ])
