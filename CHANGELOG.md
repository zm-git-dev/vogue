# Change Log

This change log will document the notable changes to this project in this file and it is following [Semantic Versioning](https://semver.org/)

## [x.x.x]

### Changed
- Added posibility to run vogue with config as environment vareable
- Removing environment vareable dependency and instead adding option for config in cli.
- Squashed the load document functions into one general function
- setting werkzeug<1.0.0 in requirements.txt
- Update genologic to 0.4.6

### Added
- code owners
- PR template
- A new index collection to the database
- A new index category collection to the database
- CLI for loading index data from lims into the index collection
- CLI for loading index category data from lims into the index category collection
- Two front end views for visualization of index data

## [1.0.0]
First initial release of Vogue according to main am doc 1980:1 and validation am doc 2035:2 

### Added
- Index view
- Turn around times
- Samples
- Preps microbial
- Preps WGS Illumina PCR-free
- Preps Lucigen PCR-free
- Preps Targeted Enrichment
- Sequencing
- Rare Disease - QC over time
- Rare Disease QC-QC
- Microbial  ST
- Microbial QC over time
- Microbial Untyped
- Microbial ST over time
- Genotype Sample status
- Genotype Plates

### Changed
- environment variables for mongo
