from genologics.lims import Lims
from genologics.entities import Sample, Artifact
from genologics.config import BASEURI,USERNAME,PASSWORD
from datetime import datetime as dt
import operator
lims = Lims(BASEURI,USERNAME,PASSWORD)

def get_sequence_date(sample_id: str, artifacts: list, udfs: dict):
    #process_type = 'CG002 - Sequence Aggregation' unsure wich we should use acually
    process_types = ['CG002 - Illumina Sequencing (HiSeq X)','CG002 - Illumina Sequencing (Illumina SBS)'] 
    udf = 'Passed Sequencing QC'

    if not sample.udf.get(udf):
        return None #testa!
    
    if not artifacts:
        return None #testa!
    
    final_date = None
    for art in artifacts:
        if not art.parent_process.type.name in process_types:
            continue
        if not final_date:
            final_date = art.parent_process.date_run
            continue
        if art.parent_process.date_run > final_date:
            final_date = art.parent_process.date_run
    
    return final_date #testa!

def get_sequenced_date(sample: Sample)-> dt.date:
    """Get the date when a sample passed sequencing."""

    process_types = ['CG002 - Illumina Sequencing (HiSeq X)','CG002 - Illumina Sequencing (Illumina SBS)'] #process_type = 'CG002 - Sequence Aggregation' unsure wich we should use acually
    udf = 'Passed Sequencing QC'

    if sample.udf.get(udf):
        artifacts = lims.get_artifacts(process_type = process_types, 
                                        samplelimsid = sample.id)
        if artifacts:
            final_date = artifacts[0].parent_process.date_run
            for art in artifacts:
                if art.parent_process.date_run > final_date:
                    final_date = art.parent_process.date_run
        return final_date
    return None

def get_received_date(sample: Sample)-> dt.date:
    """Get the date when a sample was received."""
    process_type = 'CG002 - Reception Control'
    udf = 'date arrived at clinical genomics'
    artifacts = lims.get_artifacts(process_type = process_type,
                                            samplelimsid = sample.id)
    for artifact in artifacts:   
        if artifact.parent_process and artifact.parent_process.udf.get(udf):
            return artifact.parent_process.udf.get(udf).isoformat()
    return None 

def get_prepared_date(sample: Sample)-> dt.date:
    """Get the last date when a sample was prepared in the lab."""
    process_type = 'CG002 - Aggregate QC (Library Validation)'
    artifacts = lims.get_artifacts(process_type=process_type, 
                                    samplelimsid = sample.id)
    if artifacts:
        final_date = artifacts[0].parent_process.date_run
        for art in artifacts:
            if art.parent_process.date_run > final_date:
                final_date = art.parent_process.date_run
        return final_date
    return None

def get_delivery_date(sample: Sample)-> dt.date:
    """Get delivery date for a sample."""
    process_type = 'CG002 - Delivery'
    artifacts = lims.get_artifacts(samplelimsid = sample.id, process_type = process_type,
                                   type = 'Analyte')
    if len(artifacts) == 1:
        return artifacts[0].parent_process.udf.get('Date delivered').isoformat()
    elif len(artifacts) > 1:
        #log.warning(f"multiple delivery artifacts found for: {lims_id}")
        return min(artifact.parent_process.udf['Date delivered'] for artifact in artifacts).isoformat()
    return None

#def get_delivered_to_invoiced(self):
        # """Get time between different time stamps."""
#        if ["delivered_at", "invoiced_at"] <= self.mongo_sample.keys():
#            try:
#                delivered_to_invoiced = self.mongo_sample["invoiced_at"] - self.mongo_sample["delivered_at"]
#                self.mongo_sample["delivered_to_invoiced"] = int(delivered_to_invoiced)
#            except:
#                pass

def get_sequenced_to_delivered(delivered_at: str, sequenced_at: str) -> int:
    if delivered_at and sequenced_at:
        try:
            delivered = dt.strptime(delivered_at,'%Y-%m-%d')
            sequenced = dt.strptime(sequenced_at,'%Y-%m-%d')
            sequenced_to_delivered = delivered - sequenced
            return sequenced_to_delivered.days
        except:
            return None

def get_prepped_to_sequenced(prepared_at: str, sequenced_at: str) -> int:
    if prepared_at and sequenced_at:
        try:
            prepared = dt.strptime(prepared_at,'%Y-%m-%d')
            sequenced = dt.strptime(sequenced_at,'%Y-%m-%d')
            prepped_to_sequenced = sequenced - prepared
            return prepped_to_sequenced.days
        except:
            return None

def get_received_to_prepped(prepared_at: str, received_at: str) -> int:
    if prepared_at and received_at:
        try:
            prepared = dt.strptime(prepared_at,'%Y-%m-%d')
            received = dt.strptime(received_at,'%Y-%m-%d')
            received_to_prepped = prepared - received
            return received_to_prepped.days
        except:
            return None

def get_received_to_delivered(delivered_at: str, received_at: str) -> int:
    if delivered_at and received_at:
        try:
            delivered = dt.strptime(delivered_at,'%Y-%m-%d')
            received = dt.strptime(received_at,'%Y-%m-%d')
            received_to_delivered = delivered - received
            return received_to_delivered.days
        except:
            return None


def _get_latest_input_artifact(step: str, lims_id: str) -> Artifact:
    """Returns the input artifact related to lims_id and the step that was latest run."""
    artifacts = lims.get_artifacts(samplelimsid = lims_id, process_type = step) 
    date_art_list = list(set([(a.parent_process.date_run, a) for a in artifacts]))
    if date_art_list:
        date_art_list.sort(key = operator.itemgetter(0))
        latest_outart = date_art_list[-1]
        for inart in latest_outart[1].input_artifact_list():
            if lims_id in [sample.id for sample in inart.samples]:
                return inart                  
    return None

def _get_latest_output_artifact(step: str, lims_id: str) -> Artifact:
    """Returns the output artifact related to lims_id and the step that was latest run."""
    artifacts = lims.get_artifacts(samplelimsid = lims_id, process_type = step, type = 'Analyte')
    date_art_list = list(set([(a.parent_process.date_run, a) for a in artifacts]))
    if date_art_list:
        date_art_list.sort()
        latest_outart = date_art_list[-1]
        return latest_outart[1]               
    return None


def get_concantration_and_nr_defrosts(application_tag: str, lims_id: str) -> dict:
    """Find the latest artifact that passed through a concentration_step and get its concentration_udf.
    Then go back in history to the latest lot_nr_step and get the lot_nr_udf from that step. --> lot_nr
    Then find all steps where the lot_nr was used. --> defrosts
    Then pick out those steps that were performed before our lot_nr_step. --> defrosts_before_latest_process
    Count defrosts_before_latest_process. --> nr_defrosts"""

    if not application_tag[0:6] in ['WGSPCF', 'WGTPCF']:
        return {}

    lot_nr_step = 'CG002 - End repair Size selection A-tailing and Adapter ligation (TruSeq PCR-free DNA)'
    concentration_step = 'CG002 - Aggregate QC (Library Validation)'
    lot_nr_udf = 'Lot no: TruSeq DNA PCR-Free Sample Prep Kit'
    concentration_udf = 'Concentration (nM)'

    concentration_art = _get_latest_input_artifact(concentration_step, lims_id)

    if concentration_art:
        concentration = concentration_art.udf.get(concentration_udf)
        lotnr = concentration_art.parent_process.udf.get(lot_nr_udf)
        defrosts = lims.get_processes(type=lot_nr_step, udf={lot_nr_udf : lotnr}) 
        defrosts_before_latest_process = []

        for defrost in defrosts:
            if defrost.date_run <= concentration_art.parent_process.date_run:
                defrosts_before_latest_process.append(defrost)

        nr_defrosts = len(defrosts_before_latest_process)
            
        return {'nr_defrosts':nr_defrosts, 'concentration':concentration, 'lotnr':lotnr}
    return {}

def get_final_conc_and_amount_dna(application_tag: str, lims_id: str) -> dict:
    """Find the latest artifact that passed through a concentration_step and get its concentration_udf.
    Then go back in history to the latest amount_step and get the amount_udf"""

    if not application_tag[0:6] in ['WGSLIF', 'WGTLIF']:
        return {}

    amount_udf = 'Amount (ng)'
    concentration_udf = 'Concentration (nM)'
    concentration_step = 'CG002 - Aggregate QC (Library Validation)'
    amount_step = 'CG002 - Aggregate QC (DNA)'

    concentration_art = _get_latest_input_artifact(concentration_step, lims_id)

    if concentration_art:

        amount_art = None
        step = concentration_art.parent_process
        while step and not amount_art:
            art = _get_latest_input_artifact(step.type.name, lims_id)
            if amount_step in [p.type.name for p in lims.get_processes(inputartifactlimsid=art.id)]:
                amount_art = art
            step = art.parent_process
        
        amount = amount_art.udf.get(amount_udf) if amount_art else None
        concentration = concentration_art.udf.get(concentration_udf)
        return {'amount' : amount, 'concentration':concentration}
    return {}


def get_microbial_library_concentration(application_tag: str, lims_id: str) -> float:
    """Check only samples with mictobial application tag.
    Get concentration_udf from concentration_step."""

    if not application_tag[3:5] == 'NX':
        return

    concentration_step = 'CG002 - Aggregate QC (Library Validation)'
    concentration_udf = 'Concentration (nM)'

    concentration_art = _get_latest_input_artifact(concentration_step, lims_id)

    if concentration_art:
        return concentration_art.udf.get(concentration_udf)
    else:
        return None


def get_library_size_pre_hyb(application_tag: str, lims_id: str) -> int:
    """Check only 'Targeted enrichment exome/panels'.
    Get size_udf from size_step."""

    if not application_tag[0:3] in ['EXO', 'EFT', 'PAN']:
        return

    size_step = 'CG002 - Amplify Adapter-Ligated Library (SS XT)'
    size_udf = 'Size (bp)'

    size_art = _get_latest_output_artifact(size_step, lims_id)

    if size_art:
        return size_art.udf.get(size_udf)
    else:
        None


def get_library_size_post_hyb(application_tag: str, lims_id: str) -> int:
    """Check only 'Targeted enrichment exome/panels'.
    Get size_udf from size_step."""

    if not application_tag[0:3] in ['EXO', 'EFT', 'PAN']:
        return

    size_step = 'CG002 - Amplify Captured Libraries to Add Index Tags (SS XT)'
    size_udf = 'Size (bp)'

    size_art = _get_latest_output_artifact(size_step, lims_id)

    if size_art:
        return size_art.udf.get(size_udf)
    else:
        return None


def build_sample(sample: Sample)-> dict: #def build_sample(sample: Sample, lims: Lims)-> dict:
    """Parse lims sample"""
    application_tag = sample.udf.get('Sequencing Analysis')

    mongo_sample = {'_id' : sample.id}
    mongo_sample['family'] = sample.udf.get('Family')
    mongo_sample['strain'] = sample.udf.get('Strain')
    mongo_sample['source'] = sample.udf.get('Source')

    conc_and_amount = get_final_conc_and_amount_dna(application_tag, sample.id)
    mongo_sample['amount'] = conc_and_amount.get('amount')
    mongo_sample['amount-concentration'] = conc_and_amount.get('concentration')

    concantration_and_nr_defrosts = get_concantration_and_nr_defrosts(application_tag, sample.id)
    mongo_sample['nr_defrosts'] = concantration_and_nr_defrosts.get('nr_defrosts')
    mongo_sample['nr_defrosts-concentration'] = concantration_and_nr_defrosts.get('concentration')
    mongo_sample['lotnr'] = concantration_and_nr_defrosts.get('lotnr')

    mongo_sample['microbial_library_concentration'] = get_microbial_library_concentration(application_tag, sample.id)
    mongo_sample['library_size_pre_hyb'] = get_library_size_pre_hyb(application_tag, sample.id)
    mongo_sample['library_size_post_hyb'] = get_library_size_post_hyb(application_tag, sample.id)

    sequenced_at = get_sequenced_date(sample)
    received_at = get_received_date(sample)
    prepared_at = get_prepared_date(sample)
    delivered_at = get_delivery_date(sample)

    mongo_sample['sequenced_date'] = sequenced_at
    mongo_sample['received_date'] = received_at
    mongo_sample['prepared_date'] = prepared_at
    mongo_sample['delivery_date'] = delivered_at
    mongo_sample['sequenced_to_delivered'] = get_sequenced_to_delivered(delivered_at, sequenced_at)
    mongo_sample['prepped_to_sequenced'] = get_prepped_to_sequenced(prepared_at, sequenced_at)
    mongo_sample['received_to_prepped'] = get_received_to_prepped(prepared_at, received_at)
    mongo_sample['received_to_delivered'] = get_received_to_delivered(delivered_at, received_at)

    for key in list(mongo_sample.keys()):
        if mongo_sample[key] is None:
            mongo_sample.pop(key)

    return mongo_sample
