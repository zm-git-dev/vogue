from datetime import datetime as dt
from vogue.build.lims_utils import (get_sequenced_date, get_number_of_days, get_output_artifact, 
                                    get_latest_input_artifact, str_to_datetime, get_received_date,
                                    get_prepared_date, get_delivery_date)


def test_get_sequenced_date_no_udfs(lims_sample, lims):
    ##GIVEN a sample without udfs

    udf = 'Passed Sequencing QC'
    assert not lims_sample.udf.get(udf)

    ##WHEN getting the sequence date

    sequenced_date = get_sequenced_date(lims_sample, lims)

    ##THEN assert sequenced_date is none

    assert sequenced_date is None

############################# get_sequenced_date ############################
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

    process = lims._add_process(date_str = date, process_type = 'CG002 - Illumina Sequencing (HiSeq X)')
    artifact = lims._add_artifact(parent_process = process, samples=[lims_sample])
    ##WHEN getting the sequence date
    sequenced_date = get_sequenced_date(lims_sample, lims)

    ##THEN assert sequenced_date is datetime

    assert sequenced_date == str_to_datetime(date)

############################# get_received_date ############################
def test_get_received_date_no_artifacts(lims_sample, lims):
    ##GIVEN a sample and a lims without artifacts
    ##WHEN getting the received date

    received_date = get_received_date(lims_sample, lims)

    ##THEN assert received_date is none
    assert received_date is None


def test_get_received_date_one_artifact(lims_sample, lims):
    ##GIVEN a lims with

    process_type = 'CG002 - Reception Control'
    udf = 'date arrived at clinical genomics'
    process = lims._add_process(date_str = '1818-01-01', process_type = process_type)
    artifact = lims._add_artifact(parent_process = process, samples=[lims_sample])
    process.udf[udf] = dt.today().date()

    ##WHEN getting the sequence date

    received_date = get_received_date(lims_sample, lims)

    ##THEN assert received_date is none
    assert received_date == str_to_datetime(dt.today().date().isoformat())

############################# get_prepared_date ############################
def test_get_prepared_date_no_artifacts(lims_sample, lims):
    ##GIVEN a sample and lims without artifacts

    ##WHEN getting the prepared date
    prepared_date = get_prepared_date(lims_sample, lims)

    ##THEN assert prepared_date is none
    assert prepared_date is None

def test_get_prepared_date_one_artifacts(lims_sample, lims):
    ##GIVEN a sample and lims one artifacts
    date = '1818-01-01'
    process_type = 'CG002 - Aggregate QC (Library Validation)'
    process = lims._add_process(date_str = date, process_type = process_type)
    artifact = lims._add_artifact(parent_process = process, samples=[lims_sample])
    
    ##WHEN getting the prepared date
    prepared_date = get_prepared_date(lims_sample, lims)

    ##THEN assert prepared_date is date string date
    assert prepared_date == str_to_datetime(date)

############################# get_delivery_date ############################
def test_get_delivery_date_no_artifacts(lims_sample, lims):
    ##GIVEN a sample and lims without artifacts

    ##WHEN getting the delivery date
    delivery_date = get_delivery_date(lims_sample, lims)

    ##THEN assert delivery_date is none
    assert delivery_date is None


def test_get_delivery_date_one_artifact(lims_sample, lims):
    ##GIVEN a sample and lims one artifacts
    process_type = 'CG002 - Delivery'
    udf = 'Date delivered'
    process = lims._add_process(date_str = '1818-01-01', process_type = process_type)
    artifact = lims._add_artifact(parent_process = process, samples=[lims_sample])
    process.udf[udf] = dt.today().date()


    ##WHEN getting the delivery date
    delivery_date = get_delivery_date(lims_sample, lims)

    ##THEN assert delivery_date == str_to_datetime(dt.today().date().isoformat())
    assert delivery_date == str_to_datetime(dt.today().date().isoformat())

############################# get_number_of_days ############################

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

############################# get_output_artifact ############################

def test_get_latest_output_artifact_no_art(lims):
    ##GIVEN a lims with no artifacts

    lims_id = 'Dummy'
    process_type = 'CG002 - Aggregate QC (Library Validation)'

    ##WHEN running _get_latest_output_artifact
    latest_output_artifact = get_output_artifact(process_type, lims_id, lims, last=True)

    ##THEN assert latest_output_artifact is none
    assert latest_output_artifact is None


def test_get_latest_output_artifact(lims, lims_sample):
    ##GIVEN a lims with three artifacts with diferent parent processes with 
    # diferent date_run dates 2018-01-01, 2018-02-01, 2018-03-01
    lims_id = lims_sample.id
    process_type = 'CG002 - Aggregate QC (Library Validation)'
    date1 = '2018-01-01'
    date2 = '2018-02-01'
    date3 = '2018-03-01'
    process1 = lims._add_process(date1, process_type)
    process2 = lims._add_process(date2, process_type)
    process3 = lims._add_process(date3, process_type)
    out_art1 = lims._add_artifact(process1, samples=[lims_sample])
    out_art2 = lims._add_artifact(process2, samples=[lims_sample])
    out_art3 = lims._add_artifact(process3, samples=[lims_sample])

    ##WHEN running _get_latest_output_artifact
    latest_output_artifact = get_output_artifact(process_type, lims_id, lims, last=True)

    ##THEN latest_output_artifact should be run on 2018-03-01
    assert latest_output_artifact.parent_process.date_run == date3

############################# get_latest_input_artifact ############################

def test_get_latest_input_artifact(lims, lims_sample, dummy_sample):
    ##GIVEN a lims with three artifacts with diferent parent processes with 
    # diferent date_run dates: 2018-01-01, 2018-02-01, 2018-03-01.
    # Where the third artifact (generated on the latest date), has two
    # input artifats. 
    # And only one of the input artifcts has a sample list with a sample with
    # sample_id = TheOne 

    sample_id = lims_sample.id
    process_type = 'CG002 - Aggregate QC (Library Validation)'
    date1 = '2018-01-01'
    date2 = '2018-02-01'
    date3 = '2018-03-01'

    process1 = lims._add_process(date1, process_type)
    process2 = lims._add_process(date2, process_type)
    process3 = lims._add_process(date3, process_type)

    out_art1 = lims._add_artifact(parent_process = process1, samples=[lims_sample])
    out_art2 = lims._add_artifact(parent_process = process2, samples=[lims_sample])
    out_art3 = lims._add_artifact(parent_process = process3, samples=[lims_sample])

    sample1 = lims._add_sample(sample_id = sample_id)
    sample2 = lims._add_sample(sample_id = dummy_sample.id)

    in_art1 = lims._add_artifact(samples = [lims_sample])
    in_art2 = lims._add_artifact(samples = [dummy_sample])

    out_art3.input_list = [in_art1, in_art2]

    ##WHEN running _get_latest_input_artifact
    latest_input_artifact = get_latest_input_artifact(process_type, sample_id, lims)

    ##THEN latest_input_artifact should be in_art1
    assert latest_input_artifact == in_art1
