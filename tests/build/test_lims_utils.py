from datetime import datetime as dt
from vogue.build.lims_utils import get_sequenced_date, get_number_of_days, _get_latest_output_artifact


def test_get_sequenced_date_no_udfs(lims_sample, lims):
    ##GIVEN a sample without udfs

    udf = 'Passed Sequencing QC'
    assert not lims_sample.udf.get(udf)

    ##WHEN getting the sequence date

    sequenced_date = get_sequenced_date(lims_sample, lims)

    ##THEN assert sequenced_date is none

    assert sequenced_date is None


def test_get_sequenced_date_no_artifacts(lims_sample, lims):
    ##GIVEN a sample with udf: 'Passed Sequencing QC' and a lims without artifacts
    udf = 'Passed Sequencing QC'
    date = '18-12-31'

    lims_sample.udf[udf] = date
    assert lims_sample.udf.get(udf) == date

    ##WHEN getting the sequence date

    sequenced_date = get_sequenced_date(lims_sample, lims)

    ##THEN assert sequenced_date is none

    assert sequenced_date is None

def test_get_sequenced_date_one_artifact(lims_sample, lims):
    ##GIVEN a sample with udf: 'Passed Sequencing QC' and a lims with an artifact
    udf = 'Passed Sequencing QC'
    date = '2018-12-31'

    lims_sample.udf[udf] = date
    assert lims_sample.udf.get(udf) == date

    process = lims._add_process(date_str = date)
    artifact = lims._add_artifact(process)
    ##WHEN getting the sequence date

    sequenced_date = get_sequenced_date(lims_sample, lims)

    ##THEN assert sequenced_date is datetime

    assert isinstance(sequenced_date, dt)


def test_get_number_of_days_no_date():
    ##GIVEN a date that is None
    first_date = None
    second_date = dt.today()

    ##WHEN counting the number of days between two dates
    nr_days = get_number_of_days(first_date, second_date)

    ##THEN assert nr_days is none
    assert nr_days is None


def test_get_number_of_days():
    ##GIVEN two date time dates differing by two days
    first_date = dt.strptime('2018-05-31', '%Y-%m-%d')
    second_date = dt.strptime('2018-06-02', '%Y-%m-%d')

    ##WHEN counting the number of days between two dates
    nr_days = get_number_of_days(first_date, second_date)

    ##THEN assert nr_days == 2
    assert nr_days == 2


def test_get_latest_output_artifact_no_art(lims):
    ##GIVEN a lims with no artifacts

    lims_id = 'Dummy'
    process_type = 'CG002 - Aggregate QC (Library Validation)'

    ##WHEN running _get_latest_output_artifact
    latest_output_artifact = _get_latest_output_artifact(process_type, lims_id, lims)

    ##THEN assert latest_output_artifact is none
    assert latest_output_artifact is None


def test_get_latest_output_artifact(lims):
    ##GIVEN a lims with three artifacts with diferent parent processes with 
    # diferent date_run dates 2018-01-01, 2018-02-01, 2018-03-01
    lims_id = 'Dummy'
    process_type = 'CG002 - Aggregate QC (Library Validation)'
    date1 = '2018-01-01'
    date2 = '2018-02-01'
    date3 = '2018-03-01'
    process1 = lims._add_process(date1, process_type)
    process2 = lims._add_process(date2, process_type)
    process3 = lims._add_process(date3, process_type)
    artifact1 = lims._add_artifact(process1)
    artifact2 = lims._add_artifact(process2)
    artifact3 = lims._add_artifact(process3)

    ##WHEN running _get_latest_output_artifact
    latest_output_artifact = _get_latest_output_artifact(process_type, lims_id, lims)

    ##THEN latest_output_artifact should be run on 2018-03-01
    assert latest_output_artifact.parent_process.date_run == date3


