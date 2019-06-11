from genologics.lims import Lims
from genologics.entities import Sample, Artifact

from datetime import datetime as dt
import operator
import logging
LOG = logging.getLogger(__name__)


def str_to_datetime(date: str)-> dt:
    if date is None:
        return None
    return dt.strptime(date, '%Y-%m-%d')


def get_sequenced_date(sample: Sample, lims: Lims)-> dt:
    """Get the date when a sample passed sequencing.
    
    This will return the last time that the sample passed sequencing.
    """

    process_types = ['CG002 - Illumina Sequencing (HiSeq X)', 
                     'CG002 - Illumina Sequencing (Illumina SBS)']  
    udf = 'Passed Sequencing QC'

    sample_udfs = sample.udf.get(udf)
    if not sample_udfs:
        return None

    final_date = None
    # Get the last atrtifact
    artifact = get_output_artifact(process_types=process_types, lims_id=sample.id, lims=lims, last=True)
    if artifact:
        final_date = str_to_datetime(artifact.parent_process.date_run)

    return final_date
    

def get_received_date(sample: Sample, lims: Lims)-> dt:
    """Get the date when a sample was received.
    
    Here we do not consider first or latest parent process.
    Assumption is that there is only one received date.
    """

    process_types = ['CG002 - Reception Control']
    udf = 'date arrived at clinical genomics'
    artifact = get_output_artifact(process_types = process_types, lims_id = sample.id, lims=lims, last=False)

    datetime_arrived = None
    # This is a datetime.date object
    date_arrived = None
    if artifact:
        date_arrived = artifact.parent_process.udf.get(udf)
    if date_arrived:
        # We need to convert datetime.date to datetime.datetime
        datetime_arrived = str_to_datetime(date_arrived.isoformat())

    return datetime_arrived 

def get_prepared_date(sample: Sample, lims: Lims)-> dt:
    """Get the first date when a sample was prepared in the lab.
    """
    process_types = ['CG002 - Aggregate QC (Library Validation)']

    artifact = get_output_artifact(process_types=process_types, lims_id=sample.id, lims=lims, last=False)

    prepared_date = None
    if artifact:
        prepared_date = str_to_datetime(artifact.parent_process.date_run)

    return prepared_date

def get_delivery_date(sample: Sample, lims: Lims)-> dt:
    """Get delivery date for a sample.
    
    This will return the first time a sample was delivered
    """

    process_types = ['Delivery v1', 'Delivery']
    udf = 'Date delivered'
    
    artifact = get_output_artifact(process_types=process_types, lims_id=sample.id, lims=lims, last=False)
    delivery_date = None
    
    art_date = None
    if artifact:
        art_date = artifact.parent_process.udf.get(udf)
    
    if art_date:
        # We need to convert datetime.date to datetime.datetime
        delivery_date = str_to_datetime(art_date.isoformat())

    return delivery_date


def get_number_of_days(first_date: dt, second_date : dt) -> int:
    """Get number of days between different time stamps."""

    days = None
    if first_date and second_date:
        time_span = second_date - first_date
        days = time_span.days

    return days

def get_output_artifact(process_types: list, lims_id: str, lims: Lims, last: bool = True) -> Artifact:
    """Returns the output artifact related to lims_id and the step that was first/latest run.
    
    If last = False return the first artifact
    """
    artifacts = lims.get_artifacts(samplelimsid = lims_id, process_type = process_types)
    artifact = None
    date = None
    for art in artifacts:
        # Get the date of the artifact
        new_date = str_to_datetime(art.parent_process.date_run)
        if not new_date:
            continue
        # If this is the first artifact we initialise the variables
        if not date:
            date = new_date
        if not artifact:
            artifact = art
            continue
        # If we want the latest artifact check if new date is newer than existing
        if last:
            if new_date > date:
                artifact = art
                date = new_date
        # If we want the first artifact check if new date is older than existing
        else:
            if new_date < date:
                artifact = art
                date = new_date

    return artifact


def get_latest_input_artifact(process_type: str, lims_id: str, lims: Lims) -> Artifact:
    """Returns the input artifact related to lims_id and the step that was latest run."""

    latest_input_artifact = None
    artifacts = lims.get_artifacts(samplelimsid = lims_id, process_type = process_type) 
    # Make a list of tuples (<date the artifact was generated>, <artifact>): 
    date_art_list = list(set([(a.parent_process.date_run, a) for a in artifacts]))
    if date_art_list:
        #Sort on date:
        date_art_list.sort(key = operator.itemgetter(0))
        #Get latest:
        dummy, latest_outart = date_art_list[-1] #get latest
        #Get the input artifact related to our sample
        for inart in latest_outart.input_artifact_list():
            if lims_id in [sample.id for sample in inart.samples]:
                latest_input_artifact = inart 
                break        

    return latest_input_artifact


def get_concentration_and_nr_defrosts(application_tag: str, lims_id: str, lims: Lims) -> dict:
    """Get concentration and nr of defrosts for wgs illumina PCR-free samples.

    Find the latest artifact that passed through a concentration_step and get its 
    concentration_udf. --> concentration
    Go back in history to the latest lot_nr_step and get the lot_nr_udf from that step. --> lotnr
    Find all steps where the lot_nr was used. --> all_defrosts
    Pick out those steps that were performed before our lot_nr_step --> defrosts_before_this_process
    Count defrosts_before_this_process. --> nr_defrosts"""

    if not application_tag:
        return {}

    if not application_tag[0:6] in ['WGSPCF', 'WGTPCF']:
        return {}

    lot_nr_step = 'CG002 - End repair Size selection A-tailing and Adapter ligation (TruSeq PCR-free DNA)'
    concentration_step = 'CG002 - Aggregate QC (Library Validation)'
    lot_nr_udf = 'Lot no: TruSeq DNA PCR-Free Sample Prep Kit'
    concentration_udf = 'Concentration (nM)'

    return_dict = {}
    concentration_art = get_latest_input_artifact(concentration_step, lims_id, lims)
    if concentration_art:
        concentration = concentration_art.udf.get(concentration_udf)
        lotnr = concentration_art.parent_process.udf.get(lot_nr_udf)
        this_date = str_to_datetime(concentration_art.parent_process.date_run)

        # Ignore if multiple lot numbers:
        if lotnr and len(lotnr.split(',')) == 1 and len(lotnr.split(' ')) == 1:
            all_defrosts = lims.get_processes(type = lot_nr_step, udf = {lot_nr_udf : lotnr})
            defrosts_before_this_process = []

            # Find the dates for all processes where the lotnr was used (all_defrosts),
            # and pick the once before or equal to this_date
            for defrost in all_defrosts:  
                if str_to_datetime(defrost.date_run) <= this_date:
                    defrosts_before_this_process.append(defrost)

            nr_defrosts = len(defrosts_before_this_process)

            return_dict = {'nr_defrosts' : nr_defrosts, 'concentration' : concentration, 
                            'lotnr' : lotnr, 'concentration_date' : this_date}

    return return_dict


def get_final_conc_and_amount_dna(application_tag: str, lims_id: str, lims: Lims) -> dict:
    """Find the latest artifact that passed through a concentration_step and get its 
    concentration. Then go back in history to the latest amount_step and get the amount."""

    if not application_tag:
        return {}

    if not application_tag[0:6] in ['WGSLIF', 'WGTLIF']:
        return {}

    return_dict = {}
    amount_udf = 'Amount (ng)'
    concentration_udf = 'Concentration (nM)'
    concentration_step = 'CG002 - Aggregate QC (Library Validation)'
    amount_step = 'CG002 - Aggregate QC (DNA)'

    concentration_art = get_latest_input_artifact(concentration_step, lims_id, lims)
    if concentration_art:
        amount_art = None
        step = concentration_art.parent_process
        # Go back in history untill we get to an output artifact from the amount_step
        while step and not amount_art:
            art = get_latest_input_artifact(step.type.name, lims_id, lims)
            if amount_step in [p.type.name for p in lims.get_processes(inputartifactlimsid=art.id)]:
                amount_art = art
            step = art.parent_process
        
        amount = amount_art.udf.get(amount_udf) if amount_art else None
        concentration = concentration_art.udf.get(concentration_udf)
        return_dict = {'amount' : amount, 'concentration':concentration}

    return return_dict


def get_microbial_library_concentration(application_tag: str, lims_id: str, lims: Lims) -> float:
    """Check only samples with mictobial application tag.
    Get concentration_udf from concentration_step."""

    if not application_tag:
        return {}

    if not application_tag[3:5] == 'NX':
        return None

    concentration_step = 'CG002 - Aggregate QC (Library Validation)'
    concentration_udf = 'Concentration (nM)'

    concentration_art = get_latest_input_artifact(concentration_step, lims_id, lims)

    if concentration_art:
        return concentration_art.udf.get(concentration_udf)
    else:
        return None



# The following two functions will get the udf Size (bp) that in fact is set on the 
# aggregate qc librar validation step.
# But since the same qc protocol is used both for pre-hyb and post-hyb, there is no way to 
# distiguish from within the aggregation step, wether it is pre-hyb or post-hyb qc. 
# Because of that, we instead look for the inpus atrifact to the aggregation step. 
# For pre hyb, the input artifact will come from 'CG002 - Amplify Adapter-Ligated Library (SS XT)'. 
# For post hyb, it will come from 'CG002 - Amplify Captured Libraries to Add Index Tags (SS XT)'.

def get_library_size_pre_hyb(application_tag: str, lims_id: str, lims: Lims) -> int:
    """Check only 'Targeted enrichment exome/panels'.
    Get size_udf from size_step."""

    if not application_tag:
        return None

    if not application_tag[0:3] in ['EXO', 'EFT', 'PAN']:
        return None

    size_step = ['CG002 - Amplify Adapter-Ligated Library (SS XT)']
    size_udf = 'Size (bp)'

    size_art = get_output_artifact(size_step, lims_id, lims, last=True)

    if size_art:
        return size_art.udf.get(size_udf)
    else:
        return None


def get_library_size_post_hyb(application_tag: str, lims_id: str, lims: Lims) -> int:
    """Check only 'Targeted enrichment exome/panels'.
    Get size_udf from size_step."""

    if not application_tag:
        return None

    if not application_tag[0:3] in ['EXO', 'EFT', 'PAN']:
        return None

    size_step = ['CG002 - Amplify Captured Libraries to Add Index Tags (SS XT)']
    size_udf = 'Size (bp)'

    size_art = get_output_artifact(size_step, lims_id, lims, last=True)

    if size_art:
        return size_art.udf.get(size_udf)
    else:
        return None
