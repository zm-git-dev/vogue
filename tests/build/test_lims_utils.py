from datetime import datetime as dt
from vogue.build.lims_utils import get_sequenced_date, get_number_of_days


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

def test_get_sequenced_date_one_artifact(lims_sample, lims, simple_artifact):
    ##GIVEN a sample with udf: 'Passed Sequencing QC' and a lims with an artifact
    udf = 'Passed Sequencing QC'
    date = '18-12-31'

    lims_sample.udf[udf] = date
    assert lims_sample.udf.get(udf) == date

    lims._add_artifact(simple_artifact)
    ##WHEN getting the sequence date

    sequenced_date = get_sequenced_date(lims_sample, lims)

    ##THEN assert sequenced_date is none

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
    ##GIVEN a two date time dates differing by two days
    first_date = dt.strptime('2018-05-31', '%Y-%m-%d')
    second_date = dt.strptime('2018-06-02', '%Y-%m-%d')

    ##WHEN counting the number of days between two dates
    nr_days = get_number_of_days(first_date, second_date)

    ##THEN assert nr_days == 2
    assert nr_days == 2


    

