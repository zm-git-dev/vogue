
MASTER_STEPS_UDFS = {
    'received_step': {
        'CG002 - Reception Control (Dev)': 'date arrived at clinical genomics',
        'CG002 - Reception Control': 'date arrived at clinical genomics',
        'Reception Control TWIST v1': 'date arrived at clinical genomics',
    },
    'prepared_step': {
        'CG002 - Aggregate QC (Library Validation) (Dev)',
        'CG002 - Aggregate QC (Library Validation)',
        'Aggregate QC (Library Validation) TWIST v1',
    },
    'delivery_step': {
        'CG002 - Delivery': 'Date delivered',
        'Delivery v1': 'Date delivered',
    },
    'sequenced_step': {
        'CG002 - Illumina Sequencing (HiSeq X)': 'Finish Date',
        'CG002 - Illumina Sequencing (Illumina SBS)': 'Finish Date',
        'AUTOMATED - NovaSeq Run': None,
    },
    'capture_kit_step': {
        'obsolete_CG002 - Hybridize Library  (SS XT)': 'SureSelect capture library/libraries used',
        'Hybridize Library TWIST v1': 'Bait Set',
    },
    'prep_method_step': {
        'CG002 - End repair Size selection A-tailing and Adapter ligation (TruSeq PCR-free DNA)':
        {
            'method_number': 'Method document',
            'method_version': 'Method document version',
        },
        'obsolete_CG002 - Hybridize Library  (SS XT)':
        {
            'method_number': 'Method document',
            'method_version': 'Method document versio',
        },
        'CG002 - Microbial Library Prep (Nextera)':
        {
            'method_number': 'Method',
            'method_version': 'Method Version',
        },
        'End-Repair and A-tailing TWIST v1':
        {
            'method_number': 'Method document',
            'method_version': 'Document version',
        },
    },
    'sequencing_method_step': {
        'CG002 - Cluster Generation (HiSeq X)':
        {
            'method_number': 'Method',
            'method_version': 'Version',
        },
        'CG002 - Cluster Generation (Illumina SBS)':
        {
            'method_number': 'Method Document 1',
            'method_version': 'Document 1 Version',
        },
    },
    'delivery_method_step': {
        'CG002 - Delivery':
        {
            'method_number': 'Method Document',
            'method_version': 'Method Version',
        },
        'Delivery v1':
        {
            'method_number': 'Method Document',
            'method_version': 'Method Version',
        },
    },
}




VIEWS: {
    'preps_microbial':{},
    'preps_wgs_pcr_free':{},
    'preps_lucigen_pcr_free':{},
    'preps_target_enrichmet':{},
    'dates':{},
}

PROCESSES = {
    'sequenced_date': 'AUTOMATED - NovaSeq Run',
}
