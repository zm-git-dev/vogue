from typing import List

from genologics.lims import Lims
from genologics.entities import Sample, Artifact
from vogue.constants.lims_constants import MASTER_STEPS_UDFS
from datetime import time, datetime as dt
import operator
import logging

LOG = logging.getLogger(__name__)


def str_to_datetime(date: str) -> dt:
    """Convert str to datetime"""
    if date is None:
        return None
    return dt.strptime(date, '%Y-%m-%d')


def datetime2date(date: dt) -> dt.date:
    """Convert datetime.datetime to datetime.date"""

    if date is None:
        return None
    return dt(date.year, date.month, date.day)


def get_number_of_days(first_date: dt, second_date: dt) -> int:
    """Get number of days between different time stamps."""

    days = None
    if first_date and second_date:
        time_span = second_date - first_date
        days = time_span.days

    return days


def get_output_artifact(process_types: list,
                        lims_id: str,
                        lims: Lims,
                        last: bool = True) -> Artifact:
    """Returns the output artifact related to lims_id and the step that was first/latest run.
    
    If last = False return the first artifact
    """
    artifacts = lims.get_artifacts(samplelimsid=lims_id,
                                   process_type=process_types)
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


def get_latest_input_artifact(process_type: str, lims_id: str,
                              lims: Lims) -> Artifact:
    """Returns the input artifact related to lims_id and the step that was latest run."""
    latest_input_artifact = None
    artifacts = lims.get_artifacts(samplelimsid=lims_id,
                                   process_type=process_type)
    # Make a list of tuples (<date the artifact was generated>, <artifact>):
    date_art_list = list(
        set([(a.parent_process.date_run, a) for a in artifacts]))
    if date_art_list:
        # Sort on date:
        date_art_list.sort(key=operator.itemgetter(0))
        # Get latest:
        dummy, latest_outart = date_art_list[-1]  # get latest
        # Get the input artifact related to our sample
        for inart in latest_outart.input_artifact_list():
            if lims_id in [sample.id for sample in inart.samples]:
                latest_input_artifact = inart
                break

    return latest_input_artifact


def get_concentration_and_nr_defrosts(application_tag: str, lims_id: str,
                                      lims: Lims) -> dict:
    """Get concentration and nr of defrosts for wgs illumina PCR-free samples.

    Find the latest artifact that passed through a concentration_step and get its 
    concentration_udf. --> concentration
    Go back in history to the latest lot_nr_step and get the lot_nr_udf from that step. --> lotnr
    Find all steps where the lot_nr was used. --> all_defrosts
    Pick out those steps that were performed before our lot_nr_step --> defrosts_before_this_process
    Count defrosts_before_this_process. --> nr_defrosts"""

    if not application_tag:
        return {}

    if not application_tag[0:6] in MASTER_STEPS_UDFS[
        'concentration_and_nr_defrosts']['apptags']:
        return {}

    lot_nr_steps = MASTER_STEPS_UDFS['concentration_and_nr_defrosts'][
        'lot_nr_step']
    concentration_step = MASTER_STEPS_UDFS['concentration_and_nr_defrosts'][
        'concentration_step']
    lot_nr_udf = MASTER_STEPS_UDFS['concentration_and_nr_defrosts'][
        'lot_nr_udf']
    concentration_udf = MASTER_STEPS_UDFS['concentration_and_nr_defrosts'][
        'concentration_udf']

    return_dict = {}
    concentration_art = get_latest_input_artifact(concentration_step, lims_id,
                                                  lims)
    if concentration_art:
        concentration = concentration_art.udf.get(concentration_udf)
        lotnr = concentration_art.parent_process.udf.get(lot_nr_udf)
        this_date = str_to_datetime(concentration_art.parent_process.date_run)

        # Ignore if multiple lot numbers:
        if lotnr and len(lotnr.split(',')) == 1 and len(lotnr.split(' ')) == 1:
            all_defrosts = []
            for step in lot_nr_steps:
                all_defrosts += lims.get_processes(type=step,
                                                   udf={lot_nr_udf: lotnr})
            defrosts_before_this_process = []

            # Find the dates for all processes where the lotnr was used (all_defrosts),
            # and pick the once before or equal to this_date
            for defrost in all_defrosts:
                if defrost.date_run and str_to_datetime(
                        defrost.date_run) <= this_date:
                    defrosts_before_this_process.append(defrost)

            nr_defrosts = len(defrosts_before_this_process)

            return_dict = {
                'nr_defrosts': nr_defrosts,
                'concentration': concentration,
                'lotnr': lotnr,
                'concentration_date': this_date
            }

    return return_dict


def get_final_conc_and_amount_dna(application_tag: str, lims_id: str,
                                  lims: Lims) -> dict:
    """Find the latest artifact that passed through a concentration_step and get its 
    concentration. Then go back in history to the latest amount_step and get the amount."""

    if not application_tag:
        return {}

    if not application_tag[0:6] in MASTER_STEPS_UDFS[
        'final_conc_and_amount_dna']['apptags']:
        return {}

    return_dict = {}
    amount_udf = MASTER_STEPS_UDFS['final_conc_and_amount_dna']['amount_udf']
    concentration_udf = MASTER_STEPS_UDFS['final_conc_and_amount_dna'][
        'concentration_udf']
    concentration_step = MASTER_STEPS_UDFS['final_conc_and_amount_dna'][
        'concentration_step']
    amount_step = MASTER_STEPS_UDFS['final_conc_and_amount_dna']['amount_step']

    concentration_art = get_latest_input_artifact(concentration_step, lims_id,
                                                  lims)

    if concentration_art:
        amount_art = None
        step = concentration_art.parent_process
        # Go back in history untill we get to an output artifact from the amount_step
        while step and not amount_art:
            art = get_latest_input_artifact(step.type.name, lims_id, lims)
            processes = [
                p.type.name
                for p in lims.get_processes(inputartifactlimsid=art.id)
            ]
            for step in amount_step:
                if step in processes:
                    amount_art = art
                    break
            step = art.parent_process

        amount = amount_art.udf.get(amount_udf) if amount_art else None
        concentration = concentration_art.udf.get(concentration_udf)
        return_dict = {'amount': amount, 'concentration': concentration}

    return return_dict


def get_microbial_library_concentration(application_tag: str, lims_id: str,
                                        lims: Lims) -> float:
    """Check only samples with mictobial application tag.
    Get concentration_udf from concentration_step."""

    if not application_tag:
        return {}

    if not application_tag[3:5] == MASTER_STEPS_UDFS[
        'microbial_library_concentration']['apptags']:
        return None

    concentration_step = MASTER_STEPS_UDFS['microbial_library_concentration'][
        'concentration_step']
    concentration_udf = MASTER_STEPS_UDFS['microbial_library_concentration'][
        'concentration_udf']

    concentration_art = get_latest_input_artifact(concentration_step, lims_id,
                                                  lims)

    if concentration_art:
        return concentration_art.udf.get(concentration_udf)
    else:
        return None


def get_library_size(sample_id: str, lims: Lims, size_steps: List[str], workflow: str) -> int:
    """Getting the udf Size (bp) that in fact is set on the aggregate qc librar validation step."""

    if workflow == 'TWIST':
        out_art = get_output_artifact(size_steps, sample_id, lims, last=True)
        if out_art:
            return out_art.udf.get('Size (bp)')

    return None
