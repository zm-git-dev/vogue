from genologics.lims import Lims
from genologics.entities import Sample
from genologics.config import BASEURI,USERNAME,PASSWORD
from datetime import datetime as dt
lims = Lims(BASEURI,USERNAME,PASSWORD)


class MongoPlots():
    def __init__(self):
        self.recieved_to_delivered = {}
        self.received_samples_per_mont = {}

class MongoSample():
    def __init__(self,lims_sample_id):
        self.lims_id = lims_sample_id
        self.mongo_sample = {'lims_id':lims_sample_id}
        self.lims_sample = Sample(lims,id = lims_sample_id)
        self.udfs = self.lims_sample.udf
        self.udf_keys = ['Strain', 'Family'] #FamilyID
        self.only_in_cg = ["ordered_at", "invoiced_at"]

    def get_sample_level_data(self):
        for key in  self.udf_keys:
            if key in self.udfs:
                self.mongo_sample[key] = self.udfs[key]

    def get_sequenced_date(self):
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

    def get_concantration_and_nr_defrosts(self):
        """Method to get nr lot_nr defrosts and concentration for a sample"""
        lot_nr_step = 'CG002 - End repair Size selection A-tailing and Adapter ligation (TruSeq PCR-free DNA)'
        concentration_step = 'CG002 - Aggregate QC (Library Validation)'
        lot_nr_udf = 'Lot no: TruSeq DNA PCR-Free Sample Prep Kit'
        concentration_udf = 'Concentration (nM)'

        lot_nr_arts = lims.get_artifacts(samplelimsid = self.lims_id, process_type = lot_nr_step)
        concentration_arts = lims.get_artifacts(samplelimsid = self.lims_id, process_type = concentration_step)
        
        if concentration_arts and lot_nr_arts:
            latest_process = concentration_arts[0].parent_process
            latest_outart = None
            latest_inart = None
            for art in concentration_arts:
                inarts = art.input_artifact_list()
                if latest_process.date_run <= art.parent_process.date_run:
                    latest_process = art.parent_process
                    latest_outart = art
                    for inart in inarts:
                        if self.lims_id in [sample.id for sample in inart.samples]:
                            latest_inart = inart
                            break
            concentration = latest_inart.udf[concentration_udf]
            lotnr = latest_inart.parent_process.udf[lot_nr_udf]

            defrosts = lims.get_processes(type=lot_nr_step, udf={lot_nr_udf : lotnr})
            
            defrosts_before_latest_process = []
            for defrost in defrosts:
                if defrost.date_run <= latest_inart.parent_process.date_run:
                    defrosts_before_latest_process.append(defrost)
            nr_defrosts_before_latest_process = len(defrosts_before_latest_process)
            if concentration and nr_defrosts_before_latest_process:
                self.mongo_sample['nr_defrosts'] = nr_defrosts_before_latest_process
                self.mongo_sample['concentration-nr_defrosts'] = concentration



                

        
