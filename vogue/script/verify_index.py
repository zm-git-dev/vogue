define_step = '24-113707'
bcl_step = '24-114007'
###
define_step = '24-113231'
bcl_step = '24-113250'

define_step = '24-111426'
bcl_step = '24-111431'
###
define_step = '24-110929'
bcl_step = '24-110936'
reagent_label = 'A07 - UDI0049'

### reads from bcl
flowcell_total_reads = 0
index_total_reads = 0
bcl = Process(lims, id=bcl_step)
for inp, outp in bcl.input_output_maps:
    if outp['output-generation-type'] != 'PerReagentLabel':
        continue
    art = outp['uri']

    if art.qc_flag == 'FAILED' or art.udf.get('# Reads') is None:
        continue
    flowcell_total_reads += art.udf.get('# Reads')
    if art.reagent_labels[0] == reagent_label:
        index_total_reads += art.udf.get('# Reads')

#target reads from define
flowcell_target_reads = 0
index_target_reads = 0
define = Process(lims, id=define_step)
for art in define.all_outputs():
    if art.type != 'Analyte':
        continue
    target_reads = art.udf.get('Reads to sequence (M)')
    if target_reads:
        flowcell_target_reads += int(target_reads) * 1000000
        if art.reagent_labels[0] == reagent_label:
            index_target_reads = int(target_reads) * 1000000

if flowcell_total_reads and index_target_reads and flowcell_target_reads:
    index_fraction = (index_total_reads / float(index_target_reads)) / (
        flowcell_total_reads / float(flowcell_target_reads))
else:
    index_fraction = None

index_total_reads
flowcell_total_reads
index_target_reads
flowcell_target_reads
index_fraction

container, lane_nr = inp['uri'].location
container.name
