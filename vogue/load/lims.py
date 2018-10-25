from genologics.lims import Lims
from genologics.entities import Sample, Artifact
from genologics.config import BASEURI,USERNAME,PASSWORD
from datetime import datetime as dt
lims = Lims(BASEURI,USERNAME,PASSWORD)


class MongoSample(dict):
    def __init__(self,lims_sample):
        self.lims_id = lims_sample.id
        self.mongo_sample = {'lims_id' : lims_sample.id}
        self.lims_sample = lims_sample
        self.udfs = self.lims_sample.udf
        self.udf_keys = ['Strain', 'Family', 'Source'] #FamilyID
        self.application_tag = self.lims_sample.udf.get("Sequencing Analysis")
        self._build()

    def _build(self):
        self.get_sample_level_data()
        self.get_concantration_and_nr_defrosts()
        self.get_final_conc_and_amount_dna()
        self.get_microbial_library_concentration()
        self.get_library_size_pre_hyb()
        self.get_library_size_post_hyb()
        self.get_sequenced_date()
        self.get_received_date()
        self.get_prepared_date()
        self.get_delivery_date()
        self.get_times()

    def get_sample_level_data(self):
        for key in  self.udf_keys:
            if key in self.udfs:
                self.mongo_sample[key] = self.udfs[key]

    def get_sequenced_date(self):
        """Get the date when a sample passed sequencing."""
        #process_type = 'CG002 - Sequence Aggregation' unsure wich we should use acually
        process_types = ['CG002 - Illumina Sequencing (HiSeq X)','CG002 - Illumina Sequencing (Illumina SBS)']
        udf = 'Passed Sequencing QC'
        if self.lims_sample.udf.get(udf):
            artifacts = lims.get_artifacts(process_type = process_types, 
                                            samplelimsid = self.lims_id)
            if artifacts:
                final_date = artifacts[0].parent_process.date_run
                for art in artifacts:
                    if art.parent_process.date_run > final_date:
                        final_date = art.parent_process.date_run
            self.mongo_sample["sequenced_at"] = final_date

    def get_received_date(self):
        """Get the date when a sample was received."""
        process_type = 'CG002 - Reception Control'
        udf = 'date arrived at clinical genomics'
        artifacts = lims.get_artifacts(process_type = process_type,
                                            samplelimsid = self.lims_id)
        for artifact in artifacts:   
            if artifact.parent_process and artifact.parent_process.udf.get(udf):
                self.mongo_sample["received_at"] = artifact.parent_process.udf.get(udf).isoformat()
                break 

    def get_prepared_date(self):
        """Get the last date when a sample was prepared in the lab."""
        process_type = 'CG002 - Aggregate QC (Library Validation)'
        artifacts = lims.get_artifacts(process_type=process_type, 
                                        samplelimsid = self.lims_id)
        if artifacts:
            final_date = artifacts[0].parent_process.date_run
            for art in artifacts:
                if art.parent_process.date_run > final_date:
                    final_date = art.parent_process.date_run
            self.mongo_sample["prepared_at"] = final_date

    def get_delivery_date(self):
        """Get delivery date for a sample."""
        process_type = 'CG002 - Delivery'
        artifacts = lims.get_artifacts(samplelimsid = self.lims_id, process_type = process_type,
                                       type = 'Analyte')
        if len(artifacts) == 1:
            self.mongo_sample["delivered_at"] = artifacts[0].parent_process.udf.get('Date delivered').isoformat()
        elif len(artifacts) > 1:
            #log.warning(f"multiple delivery artifacts found for: {lims_id}")
            self.mongo_sample["delivered_at"] = min(artifact.parent_process.udf['Date delivered'] for artifact in artifacts).isoformat()

    def get_times(self):
        """Get time between different time stamps."""
#        if ["delivered_at", "invoiced_at"] <= self.mongo_sample.keys():
#            try:
#                delivered_to_invoiced = self.mongo_sample["invoiced_at"] - self.mongo_sample["delivered_at"]
#                self.mongo_sample["delivered_to_invoiced"] = int(delivered_to_invoiced)
#            except:
#                pass
        if ["delivered_at", "sequenced_at"] <= self.mongo_sample.keys():
            try:
                delivered = dt.strptime(self.mongo_sample["delivered_at"],'%Y-%m-%d')
                sequenced = dt.strptime(self.mongo_sample["sequenced_at"],'%Y-%m-%d')
                sequenced_to_delivered = delivered - sequenced
                self.mongo_sample["sequenced_to_delivered"] = sequenced_to_delivered.days
            except:
                pass
        if ["sequenced_at", "prepared_at"] <= self.mongo_sample.keys():
            try:
                prepared = dt.strptime(self.mongo_sample["prepared_at"],'%Y-%m-%d')
                sequenced = dt.strptime(self.mongo_sample["sequenced_at"],'%Y-%m-%d')
                prepped_to_sequenced = sequenced - prepared
                self.mongo_sample["prepped_to_sequenced"] = prepped_to_sequenced.days
            except:
                pass
        if ["prepared_at", "received_at"] <= self.mongo_sample.keys():
            try:
                prepared = dt.strptime(self.mongo_sample["prepared_at"],'%Y-%m-%d')
                received = dt.strptime(self.mongo_sample["received_at"],'%Y-%m-%d')
                received_to_prepped = prepared - received
                self.mongo_sample["received_to_prepped"] = received_to_prepped.days
            except:
                pass
        if ["delivered_at", "received_at"] <= self.mongo_sample.keys():
            try:
                delivered = dt.strptime(self.mongo_sample["delivered_at"],'%Y-%m-%d')
                received = dt.strptime(self.mongo_sample["received_at"],'%Y-%m-%d')
                received_to_delivered = delivered - received
                self.mongo_sample["received_to_delivered"] = received_to_delivered.days
            except:
                pass

    def _get_latest_input_artifact(self, step: str) -> Artifact:
        """Returns the input artifact related to self.lims_id and the step that was latest run."""
        artifacts = lims.get_artifacts(samplelimsid = self.lims_id, process_type = step) 
        date_art_list = list(set([(a.parent_process.date_run, a) for a in artifacts]))
        if date_art_list:
            date_art_list.sort()
            latest_outart = date_art_list[-1]
            for inart in latest_outart[1].input_artifact_list():
                if self.lims_id in [sample.id for sample in inart.samples]:
                    return inart                  
        return None

    def _get_latest_output_artifact(self, step: str) -> Artifact:
        """Returns the output artifact related to self.lims_id and the step that was latest run."""

        artifacts = lims.get_artifacts(samplelimsid = self.lims_id, process_type = step,
                                        type = 'Analyte') 
        date_art_list = list(set([(a.parent_process.date_run, a) for a in artifacts]))
        if date_art_list:
            date_art_list.sort()
            latest_outart = date_art_list[-1]
            return latest_outart[1]               
        return None

    def get_concantration_and_nr_defrosts(self):
        """Find the latest artifact that passed through a concentration_step and get its concentration_udf.
        Then go back in history to the latest lot_nr_step and get the lot_nr_udf from that step. --> lot_nr
        Then find all steps where the lot_nr was used. --> defrosts
        Then pick out those steps that were performed before our lot_nr_step. --> defrosts_before_latest_process
        Count defrosts_before_latest_process. --> nr_defrosts"""

        if not self.application_tag[0:6] in ['WGSPCF', 'WGTPCF']:
            return

        lot_nr_step = 'CG002 - End repair Size selection A-tailing and Adapter ligation (TruSeq PCR-free DNA)'
        concentration_step = 'CG002 - Aggregate QC (Library Validation)'
        lot_nr_udf = 'Lot no: TruSeq DNA PCR-Free Sample Prep Kit'
        concentration_udf = 'Concentration (nM)'

        concentration_art = self._get_latest_input_artifact(concentration_step)

        if concentration_art:
            concentration = concentration_art.udf.get(concentration_udf)
            lotnr = concentration_art.parent_process.udf.get(lot_nr_udf)
            defrosts = lims.get_processes(type=lot_nr_step, udf={lot_nr_udf : lotnr}) 
            defrosts_before_latest_process = []

            for defrost in defrosts:
                if defrost.date_run <= concentration_art.parent_process.date_run:
                    defrosts_before_latest_process.append(defrost)

            nr_defrosts_before_latest_process = len(defrosts_before_latest_process)
            
            self.mongo_sample['nr_defrosts'] = nr_defrosts_before_latest_process or None
            self.mongo_sample['concentration-nr_defrosts'] = concentration or None
            self.mongo_sample['lot_nr'] = lotnr or None


    def get_final_conc_and_amount_dna(self):
        """Find the latest artifact that passed through a concentration_step and get its concentration_udf.
        Then go back in history to the latest amount_step and get the amount_udf"""

        if not self.application_tag[0:6] in ['WGSLIF', 'WGTLIF']:
            return

        amount_udf = 'Amount (ng)'
        concentration_udf = 'Concentration (nM)'
        concentration_step = 'CG002 - Aggregate QC (Library Validation)'
        amount_step = 'CG002 - Aggregate QC (DNA)'

        concentration_art = self._get_latest_input_artifact(concentration_step)

        if concentration_art:

            amount_art = None
            step = concentration_art.parent_process
            while step and not amount_art:
                art = self._get_latest_input_artifact(step.type.name)
                if amount_step in [p.type.name for p in lims.get_processes(inputartifactlimsid=art.id)]:
                    amount_art = art
                step = art.parent_process
        
            self.mongo_sample['amount'] = amount_art.udf.get(amount_udf) if amount_art else None
            self.mongo_sample['concentration-amount'] = concentration_art.udf.get(concentration_udf)


    def get_microbial_library_concentration(self):
        """Check only samples with mictobial application tag.
        Get concentration_udf from concentration_step."""

        if not self.application_tag[3:5] == 'NX':
            return

        concentration_step = 'CG002 - Aggregate QC (Library Validation)'
        concentration_udf = 'Concentration (nM)'

        concentration_art = self._get_latest_input_artifact(concentration_step)

        if concentration_art:
            self.mongo_sample['concentration-microbial'] = concentration_art.udf.get(concentration_udf)



    def get_library_size_pre_hyb(self):
        """Check only 'Targeted enrichment exome/panels'.
        Get size_udf from size_step."""

        if not self.application_tag[0:3] in ['EXO', 'EFT', 'PAN']:
            return

        size_step = 'CG002 - Amplify Adapter-Ligated Library (SS XT)'
        size_udf = 'Size (bp)'

        size_art = self._get_latest_output_artifact(size_step)

        if size_art:
            self.mongo_sample['sizs_bp_pre_hyb'] = size_art.udf.get(size_udf)


    def get_library_size_post_hyb(self):
        """Check only 'Targeted enrichment exome/panels'.
        Get size_udf from size_step."""

        if not self.application_tag[0:3] in ['EXO', 'EFT', 'PAN']:
            return

        size_step = 'CG002 - Amplify Captured Libraries to Add Index Tags (SS XT)'
        size_udf = 'Size (bp)'

        size_art = self._get_latest_output_artifact(size_step)

        if size_art:
            self.mongo_sample['sizs_bp_post_hyb'] = size_art.udf.get(size_udf)


                

        
