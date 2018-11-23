from datetime import datetime as dt
from vogue.build.lims_utils import (get_sequenced_date, get_number_of_days, get_output_artifact, 
                                    get_latest_input_artifact, str_to_datetime, get_received_date,
                                    get_prepared_date, get_delivery_date, get_concentration_and_nr_defrosts)


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

# def test_get_sequenced_date_one_artifact(lims_sample, lims):
#     ##GIVEN a sample with udf: 'Passed Sequencing QC' and a lims with an artifact
#     udf = 'Passed Sequencing QC'
#     date = '2018-12-31'

#     lims_sample.udf[udf] = date
#     assert lims_sample.udf.get(udf) == date

    process = lims._add_process(date_str = date, process_type = 'CG002 - Illumina Sequencing (HiSeq X)')
    artifact = lims._add_artifact(parent_process = process)
    ##WHEN getting the sequence date
    sequenced_date = get_sequenced_date(lims_sample, lims)

#     ##THEN assert sequenced_date is datetime

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
    artifact = lims._add_artifact(parent_process = process)
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
    artifact = lims._add_artifact(parent_process = process)
    
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
    artifact = lims._add_artifact(parent_process = process)
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
    out_art1 = lims._add_artifact(process1)
    out_art2 = lims._add_artifact(process2)
    out_art3 = lims._add_artifact(process3)

    ##WHEN running _get_latest_output_artifact
    latest_output_artifact = get_output_artifact(process_type, lims_id, lims, last=True)

    ##THEN latest_output_artifact should be run on 2018-03-01
    assert latest_output_artifact.parent_process.date_run == date3

############################# get_latest_input_artifact ############################

def test_get_latest_input_artifact(lims):
    ##GIVEN a lims with three artifacts with diferent parent processes with 
    # diferent date_run dates: 2018-01-01, 2018-02-01, 2018-03-01.
    # Where the third artifact (generated on the latest date), has two
    # input artifats. 
    # And only one of the input artifcts has a sample list with a sample with
    # sample_id = TheOne 

    sample_id = 'TheOne'
    process_type = 'CG002 - Aggregate QC (Library Validation)'
    date1 = '2018-01-01'
    date2 = '2018-02-01'
    date3 = '2018-03-01'

    process1 = lims._add_process(date1, process_type)
    process2 = lims._add_process(date2, process_type)
    process3 = lims._add_process(date3, process_type)

    out_art1 = lims._add_artifact(parent_process = process1)
    out_art2 = lims._add_artifact(parent_process = process2)
    out_art3 = lims._add_artifact(parent_process = process3)

    sample1 = lims._add_sample(sample_id = sample_id)
    sample2 = lims._add_sample(sample_id = 'Dummy')

    in_art1 = lims._add_artifact(samples = [sample1])
    in_art2 = lims._add_artifact(samples = [sample2])

    out_art3.input_list = [in_art1, in_art2]

    ##WHEN running _get_latest_input_artifact
    latest_input_artifact = get_latest_input_artifact(process_type, sample_id, lims)

    ##THEN latest_input_artifact should be in_art1
    assert latest_input_artifact == in_art1

def test_get_latest_input_artifact(lims):
    ##GIVEN a lims with three artifacts with diferent parent processes with 
    # diferent date_run dates: 2018-01-01, 2018-02-01, 2018-03-01.
    # Where the third artifact (generated on the latest date), has two
    # input artifats. 
    # And only one of the input artifcts has a sample list with a sample with
    # sample_id = TheOne 

<<<<<<< HEAD
    sample_id = 'TheOne'
    process_type = 'CG002 - Aggregate QC (Library Validation)'
    date1 = '2018-01-01'
    date2 = '2018-02-01'
    date3 = '2018-03-01'

    process1 = lims._add_process(date1, process_type)
    process2 = lims._add_process(date2, process_type)
    process3 = lims._add_process(date3, process_type)
=======
############################# get_concentration_and_nr_defrosts ############################
def test_get_concentration_and_nr_defrosts(lims):
    ##GIVEN a lims with no artifacts

    lotnumber = '12345'
    application_tag = 'WGSPCF'
    sample_id = 'Dummy_Samp_id'
    lot_nr_step = 'CG002 - End repair Size selection A-tailing and Adapter ligation (TruSeq PCR-free DNA)'
    concentration_step = 'CG002 - Aggregate QC (Library Validation)'
    lot_nr_udf = 'Lot no: TruSeq DNA PCR-Free Sample Prep Kit'
    concentration_udf = 'Concentration (nM)'
    sample = lims._add_sample(sample_id = sample_id)

    lot_process_1 = lims._add_process(date_str = '1919-01-01', process_type = lot_nr_step)
    lot_process_1.udf[lot_nr_udf] = lotnumber
    lot_process_2 = lims._add_process(date_str = '1819-01-01', process_type = lot_nr_step)
    lot_process_2.udf[lot_nr_udf] = lotnumber
    lot_process_3 = lims._add_process(date_str = '1719-01-01', process_type = lot_nr_step)
    lot_process_3.udf[lot_nr_udf] = lotnumber
    lot_artifact = lims._add_artifact(parent_process = lot_process_1, samples = [sample])

    lot_artifact.udf[concentration_udf] = 12
    concentration_process = lims._add_process(date_str = '1818-01-01', process_type = concentration_step)
    concentration_out_artifact = lims._add_artifact(parent_process = concentration_process, samples = [sample])
    concentration_out_artifact.input_list.append(lot_artifact)


    ##WHEN running _get_latest_output_artifact
    result_dict = get_concentration_and_nr_defrosts(application_tag, sample_id,lims)

    ##THEN assert concentration should be 12 and nr_defrosts 3
    assert result_dict['concentration'] == 12 and result_dict['nr_defrosts'] == 3



############################# get_final_conc_and_amount_dna ############################
############################# get_microbial_library_concentration ############################
############################# get_library_size_pre_hyb ############################
############################# get_library_size_post_hyb ############################


>>>>>>> another test and some corections in lims_utils.py

    out_art1 = lims._add_artifact(parent_process = process1)
    out_art2 = lims._add_artifact(parent_process = process2)
    out_art3 = lims._add_artifact(parent_process = process3)

    sample1 = lims._add_sample(sample_id = sample_id)
    sample2 = lims._add_sample(sample_id = 'Dummy')

    in_art1 = lims._add_artifact(samples = [sample1])
    in_art2 = lims._add_artifact(samples = [sample2])

    out_art3.input_list = [in_art1, in_art2]

    ##WHEN running _get_latest_input_artifact
    latest_input_artifact = _get_latest_input_artifact(process_type, sample_id, lims)

    ##THEN latest_input_artifact should be in_art1
    assert latest_input_artifact == in_art1
