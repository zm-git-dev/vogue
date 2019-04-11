"""
unittests for prepare_multiqc.py
"""

import prepare_multiqc


def test_read_multiqc():
    """
    Test reading valid json
    """
    # GIVEN a valid json
    valid_multiqc = './multiqc_data.json'

    # WHEN reading json file
    multiqc_dict = prepare_multiqc.read_multiqc(valid_multiqc)

    # THEN output should be a dictionary
    assert isinstance(multiqc_dict, dict)


def test_validate_multiqc():
    """
    Test validating multiqc json
    """
    # GIVEN a valid multiqc json file
    valid_multiqc = './multiqc_data.json'

    # WHEN reading the valid json file
    multiqc_dict = prepare_multiqc.read_multiqc(valid_multiqc)

    # THEN validation should return True
    assert prepare_multiqc.validate_multiqc(multiqc_dict)

    # GIVEN an invalid multiqc json file (but a valid json)
    invalid_multiqc = './not_a_multiqc_report.json'

    # WHEN reading the invalid multiqc json file
    multiqc_dict = prepare_multiqc.read_multiqc(invalid_multiqc)

    # THEN validation should return False
    assert not prepare_multiqc.validate_multiqc(multiqc_dict)


def test_extract_analysis():
    """
    Test extracting sample level and all information from mutliqc
    """
    # GIVEN a valid multiqc json file, all keys, and no sample
    valid_multiqc = './multiqc_data.json'
    multiqc_key = 'all'
    sample = tuple()

    # WHEN reading the valid multiqc json file
    multiqc_dict = prepare_multiqc.read_multiqc(valid_multiqc)

    # THEN output should be a non-empty dictionary
    assert prepare_multiqc.extract_analysis(multiqc_dict=multiqc_dict,
                                            json_keys=multiqc_key,
                                            samples=sample)

    # GIVEN a valid multiqc json file, all keys, and no sample
    valid_multiqc = './multiqc_data.json'
    multiqc_key = [
        'multiqc_picard_AlignmentSummaryMetrics', 'multiqc_picard_HsMetrics',
        'multiqc_picard_dups'
    ]
    sample = tuple()

    # WHEN reading the valid multiqc json file
    multiqc_dict = prepare_multiqc.read_multiqc(valid_multiqc)

    # THEN output should be a non-empty dictionary
    assert prepare_multiqc.extract_analysis(multiqc_dict=multiqc_dict,
                                            json_keys=multiqc_key,
                                            samples=sample)

    # GIVEN a valid multiqc json file, all keys, and no sample
    valid_multiqc = './multiqc_data.json'
    multiqc_key = [
        'multiqc_picard_AlignmentSummaryMetrics', 'multiqc_picard_HsMetrics',
        'multiqc_picard_dups'
    ]
    sample = tuple()

    # WHEN reading the valid multiqc json file and extracting all results
    multiqc_dict = prepare_multiqc.read_multiqc(valid_multiqc)

    # THEN output should be a non-empty dictionary
    assert prepare_multiqc.extract_analysis(multiqc_dict=multiqc_dict,
                                            json_keys=multiqc_key,
                                            samples=sample)

    # GIVEN a valid multiqc json file, all keys, and two samples
    valid_multiqc = './multiqc_data.json'
    multiqc_key = [
        'multiqc_picard_AlignmentSummaryMetrics', 'multiqc_picard_HsMetrics',
        'multiqc_picard_dups'
    ]
    sample = ('ACC5152A10_R', 'ACC5152A1_R')

    # WHEN reading the valid multiqc json file and extracting all results
    multiqc_dict = prepare_multiqc.read_multiqc(valid_multiqc)
    multiqc_dict = prepare_multiqc.extract_analysis(multiqc_dict=multiqc_dict,
                                                    json_keys='all',
                                                    samples=tuple())

    # THEN output should be a non-empty dictionary
    assert prepare_multiqc.extract_analysis(multiqc_dict=multiqc_dict,
                                            json_keys=multiqc_key,
                                            samples=sample)


def test_write_json(tmpdir):
    """
    Test writing all extracted information from multiqc
    """

    # GIVEN a valid multiqc json, validated, no sample, and extracted
    valid_multiqc = './multiqc_data.json'
    multiqc_key = 'all'
    sample = tuple()

    # WHEN reading the valid multiqc json file, and extracting all reads
    multiqc_dict = prepare_multiqc.read_multiqc(valid_multiqc)
    multiqc_dict = prepare_multiqc.extract_analysis(multiqc_dict=multiqc_dict,
                                                    json_keys=multiqc_key,
                                                    samples=sample)

    # THEN writing json output should be succesfull
    json_file_out = tmpdir.join('json_out.json')
    prepare_multiqc.write_json(multiqc_dict, json_file_out.basename,
                               json_file_out.dirname)
    assert json_file_out.read()


def test_write_json_per_sample(tmpdir):
    """
    Test writing sample level information extracted from multiqc
    """

    # GIVEN a valid multiqc json file, all keys, and two samples
    valid_multiqc = './multiqc_data.json'
    multiqc_key = [
        'multiqc_picard_AlignmentSummaryMetrics', 'multiqc_picard_HsMetrics',
        'multiqc_picard_dups'
    ]
    sample = ('ACC5152A10_R', 'ACC5152A1_R')
    base_name = 'json_out.json'
    out_tmp_file = tmpdir.join(base_name)
    dir_name = out_tmp_file.dirname

    # WHEN reading the valid multiqc json file and extracting all results
    multiqc_dict = prepare_multiqc.read_multiqc(valid_multiqc)
    multiqc_dict = prepare_multiqc.extract_analysis(multiqc_dict=multiqc_dict,
                                                    json_keys='all',
                                                    samples=tuple())
    multiqc_dict = prepare_multiqc.extract_analysis(multiqc_dict=multiqc_dict,
                                                    json_keys=multiqc_key,
                                                    samples=sample)

    # THEN writing json output should be succesfull
    prepare_multiqc.write_json_per_sample(multiqc_dict, base_name, dir_name)
    for single_sample in sample:
        json_file_out = tmpdir.join(single_sample + "." + base_name)
        assert json_file_out.read()
