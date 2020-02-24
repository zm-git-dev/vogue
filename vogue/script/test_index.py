arts=lims.get_artifacts(reagent_label="A07 - UDI0049", 
                        process_type=['Bcl Conversion & Demultiplexing (Nova Seq)'])
runs={}
for art in arts:
    if len(art.samples) != 1:
        continue
    index_reads = art.udf.get('# Reads') ############!!!!!!!!!!
    if index_reads is None or art.qc_flag == 'FAILED' or index_reads<1000:
        continue
    lane = art.input_artifact_list()[0]
    sample = art.samples[0]
    application_tag = sample.udf.get('Sequencing Analysis')
    if application_tag[0:3] in ['EXO','RML','MWX','MET', 'EXT']: ############!!!!!!!!!!
        continue
    if art.input_artifact_list():
        if art.input_artifact_list()[0].location:
            run=art.input_artifact_list()[0].location[0].name
            print(run)
            if run not in runs:
                runs[run]=[art]
            else:
                runs[run].append(art)


