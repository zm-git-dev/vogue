from vogue.build.lims import build_sample

def test_build_sample(lims_sample, lims):
    ## GIVEN a lims sample
    ## WHEN building a mongo sample
    lims_sample.udf['Sequencing Analysis'] = 'WGSLIF'
    mongo_sample = build_sample(lims_sample, lims)
    ## THEN the sample should have been parsed in the correct way
    assert mongo_sample['_id'] == lims_sample.id

def test_build_sample_family(family_sample, lims):
    ## GIVEN a lims sample with a family
    ## WHEN building a mongo sample
    mongo_sample = build_sample(family_sample, lims)
    ## THEN the sample should have been parsed in the correct way
    assert mongo_sample['family'] == family_sample.udf.get('Family')

    