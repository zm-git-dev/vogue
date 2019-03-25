from vogue.build.flowcell import build_run


def test_build_run(lims_run):
    ##GIVEN a sample without udfs
    date = 
    udf = 'Passed Sequencing QC'
    assert not lims_sample.udf.get(udf)

    ##WHEN getting the sequence date

    sequenced_date = get_sequenced_date(lims_sample, lims)

    ##THEN assert sequenced_date is none

    assert sequenced_date is None