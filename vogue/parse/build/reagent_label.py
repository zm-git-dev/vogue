from vogue.constants.lims_constants import LANE_UDFS, MASTER_STEPS_UDFS
import logging
LOG = logging.getLogger(__name__)


def filter_none(mongo_dict):
    """Function to filter out Nones and NaN from a dict."""
    for key in list(mongo_dict.keys()):
        val = mongo_dict[key]
        try:
            if val is None or math.isnan(val):
                mongo_dict.pop(key)
        except Exception:
            continue
    return mongo_dict

def get_define_step_data(bcl_step):
    """Search the artifact history for the define steps for each lane.
    Returns:
        lanes: dict
            keys: lane ids
            values: { 'lane_input': the output artifacts of the define step, 
                     'define_step': the define step }
        flowcell_target_reads: int
            the summe of the udf 'Reads to sequence (M)' from all outarts in the step"""

    LOG.info('Searching Define Steps')
    lanes = {}
    for lane in bcl_step.all_inputs(unique=True):
        process = lane.parent_process
        
        while process.type.name not in MASTER_STEPS_UDFS['reagent_labels']['steps']['define']:
            art = process.all_inputs()[0]
            process = art.parent_process

        define_step_outputs = {}
        flowcell_target_reads = 0
        
        for art in process.all_outputs():
            if art.type != 'Analyte':
                continue

            udf = MASTER_STEPS_UDFS['reagent_labels']['udfs']['target_reads']
            flowcell_target_reads += float(art.udf.get(udf, 0))

            if len(art.samples) != 1: # ignore pools
                continue
            sample_id = art.samples[0].id
            define_step_outputs[sample_id] = art
            
            
        lanes[lane.id] = {'lane_input': define_step_outputs, 'define_step': process}
    LOG.info('Found Define Steps: %s' % ', '.join(lanes.keys()))
    return lanes, flowcell_target_reads*1000000

def _get_target_reads(artifact):

    udf = MASTER_STEPS_UDFS['reagent_labels']['udfs']['target_reads']
    index_target_reads = artifact.udf.get(udf)
    if index_target_reads and index_target_reads.isnumeric():
        return int(index_target_reads)*1000000 
    else:
        return None

def reagent_label_data(lims, bcl_step):
    """This function takes as input a bcl conversion and demultiplexing step. From that step it goes
    back in artifact history to the prevoius Define step. Both step types exist in the Nova Seq 
    workflow. 
    From the output artifacts of the bcl step, index_total_reads is calculated:
        index_total_reads: the sum of '# Reads' from all artifact with a specific index
        flowcell_total_reads: the sum of '# Reads' from all output artifacts
    From the output artifacts of the define step, index_target_reads and flowcell_target_reads are fetched:
        index_target_reads: fetched from the 'Reads to sequence (M)' udf of the output artifact with a specific index 
        flowcell_target_reads: the sum of the 'Reads to sequence (M)' udf of all the output artifacts
        """

    lanes = {}
    indexes = {}
    flowcell_total_reads = 0


    for inp, outp in bcl_step.input_output_maps:
        if inp['parent-process'].type.name != 'STANDARD Prepare for Sequencing (Nova Seq)':
            continue
        
        if outp['output-generation-type'] != 'PerReagentLabel':
            continue

        lane = inp['uri']
        art = outp['uri']

        index_reads = art.udf.get(MASTER_STEPS_UDFS['reagent_labels']['udfs']['reads'])

        if index_reads is None or art.qc_flag == 'FAILED' or index_reads<1000:
            continue

        flowcell_total_reads += index_reads
        
        sample = art.samples[0]
        application_tag = sample.udf.get('Sequencing Analysis')

        if application_tag[0:2] in MASTER_STEPS_UDFS['reagent_labels']['exclue_tags']:
            continue
        
        if not lanes:
            lanes, flowcell_target_reads = get_define_step_data(bcl_step)
        
        if not sample.id in lanes[lane.id]['lane_input']:
            LOG.info('This sample whas put as a pool into the define step: ' + sample.id + ' ' + application_tag)
            continue

        index = art.reagent_labels[0]

        container, lane_nr = lane.location
        if index not in indexes:
            define_step = lanes[lane.id]['define_step']
            sample
            index_target_reads = _get_target_reads(lanes[lane.id]['lane_input'][sample.id])
            indexes[index] = {
                '_id': '_'.join([index, container.name]),
                'url': index.replace(' ',''),
                'index_total_reads': index_reads,
                'index_target_reads': index_target_reads,
                'flowcell_target_reads': flowcell_target_reads,
                'index': index,
                'sample': sample.id,
                'lanes': {lane_nr: dict(art.udf.items())},
                'flowcell_id': container.name,
                'flowcell_type': container.type.name,
                'define_step_udfs': dict(define_step.udf.items()),
                'define_step_id': define_step.id,
                'bcl_step_id': bcl_step.id
                }
        else:
            indexes[index]['lanes'][lane_nr] = dict(art.udf.items())
            indexes[index]['index_total_reads'] += index_reads

    for index , data in indexes.items():
        data['flowcell_total_reads'] = flowcell_total_reads
        indexes[index] = filter_none(data)

    return indexes
