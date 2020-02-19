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

def get_define_step(lane):
    """Search the artifact history for the define step.
    Returns:
     define_step_outputs: the output artifacts of the define step, 
     process: the define step 
     flowcell_target_reads: the summe of the udf 'Reads to sequence (M)' from all outarts in the step"""

    process = lane.parent_process
    while process.type.name != 'Define Run Format and Calculate Volumes (Nova Seq)': ##########!!!!!!!!!!!
        art = process.all_inputs()[0]
        process = art.parent_process

    define_step_outputs = {}
    flowcell_target_reads = 0
    for art in process.all_outputs():
        flowcell_target_reads += float(art.udf.get('Reads to sequence (M)', 0))  ##########!!!!!!!!!!!
        if len(art.samples) !=1: # ignore pools
            continue
        define_step_outputs[art.samples[0].id] = art
    return define_step_outputs, process, flowcell_target_reads*1000000


def index_data(bcl_step):
    """This function takes as input a bcl conversion and demultiplexing step. From that step it goas
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
    bcl_artifacts = bcl_step.all_outputs(unique=True)

    for art in bcl_artifacts:
        if len(art.samples) != 1:
            continue

        index_reads = art.udf.get('# Reads') ############!!!!!!!!!!

        if index_reads is None or art.qc_flag == 'FAILED' or index_reads<1000:
            continue

        flowcell_total_reads += index_reads
        lane = art.input_artifact_list()[0]
        sample = art.samples[0]
        application_tag = sample.udf.get('Sequencing Analysis')

        if application_tag[0:3] in ['EXO','RML','MWX','MET', 'EXT']: ############!!!!!!!!!!
            continue

        if not lanes:
            LOG.info('Searching Define Step')
            for lane in bcl_step.all_inputs():
                lane_input, define_step, flowcell_target_reads = get_define_step(lane)
                lanes[lane.id] = {'lane_input': lane_input, 'define_step': define_step}
            LOG.info('Done!')

        if not sample.id in lanes[lane.id]['lane_input']:
            LOG.info('This sample whas put as a pool into the define step: ' + sample.id + ' ' + application_tag)
            continue

        define_step = lanes[lane.id]['define_step']
        lane_input = lanes[lane.id]['lane_input'][sample.id]
        reads_to_sequence = lane_input.udf.get('Reads to sequence (M)') ############!!!!!!!!!!
        reads_to_sequence = int(reads_to_sequence)*1000000 if reads_to_sequence.isnumeric() else None
        index = lane_input.reagent_labels[0]
        container, lane = lane.location

        if index not in indexes:
            indexes[index] = {
                '_id': '_'.join([index, container.name]),
                'url': index.replace(' ',''),
                'index_total_reads': index_reads,
                'index_target_reads': reads_to_sequence,
                'flowcell_target_reads': flowcell_target_reads,
                'index': index,
                'sample': sample.id,
                'lanes': {lane: dict(art.udf.items())},
                'flowcell_id': container.name,
                'flowcell_type': container.type.name,
                'define_step_udfs': dict(define_step.udf.items()),
                'define_step_id': define_step.id,
                'bcl_step_id': bcl_step.id
                }
        else:
            indexes[index]['lanes'][lane] = dict(art.udf.items())
            indexes[index]['index_total_reads'] += index_reads
    for index in indexes:
        indexes[index]['flowcell_total_reads'] = flowcell_total_reads

    for index , data in indexes.items():
        indexes[index] = filter_none(data)

    return indexes
