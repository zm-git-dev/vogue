ANALYSIS_DESC = {
    "multiqc": "General quality control metrics for post- and pre-variant calling prepared by multiqc",
    "microsalt": "Results and quality control metrics output from microsalt workflow",
}

ANALYSIS_SETS = {
    "multiqc": {
        "multiqc_picard_dups": "multiqc json/yaml report key for picard mark duplicate.",
        "multiqc_picard_HsMetrics": "multiqc json/yaml report key for picard collecthsmetrics.",
        "multiqc_picard_AlignmentSummaryMetrics": "multiqc json/yaml report key for picard alignment summary metrics",
        "multiqc_picard_insertSize": "multiqc json/yaml report key for picard insert size metrics",
    },
    "microsalt": {
        "blast_pubmlst": "results for blasting for molecular typing and microbial genome diversity against pubmslt database",
        "quast_assembly": "results for quality assessment tool for genome assemblies (quast)",
        "blast_resfinder_resistence": "results blasting against the resistance database provided by resfinder db",
        "picard_markduplicate": "quality control and marking duplicate reads in bam/sam files",
        "microsalt_samtools_stats": "quality control to collect statistics from bam files",
    },
}
