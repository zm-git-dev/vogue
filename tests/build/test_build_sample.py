from vogue.build.sample import build_sample
from vogue.adapter.plugin import VougeAdapter


def test_build_sample(lims_sample, lims, database):
    # GIVEN a lims sample with a valid application tag
    #  and a database with application tags
    database.application_tag.update_one({'_id' : 'WGSPCFC030'}, {'$set' : {"category" : "wgs"}},
                                         upsert=True)
    lims_sample.udf['Sequencing Analysis'] = 'WGSPCFC030'
    adapter = VougeAdapter(database.client, db_name = database.name)

    # WHEN building a mongo sample
    mongo_sample = build_sample(lims_sample, lims, adapter)
    

    # THEN the sample should have been parsed in the correct way
    assert mongo_sample['category'] == 'wgs'
    assert mongo_sample['_id'] == lims_sample.id
    assert mongo_sample['category'] == 'wgs'


def test_build_sample_no_apptag(lims_sample, lims, database):
    # GIVEN a lims sample with missing application tag
    #  and a database with application tags
    database.application_tag.update_one({'_id' : 'WGSPCFC030'}, {'$set' : {"category" : "wgs"}},
                                         upsert=True)
    
    adapter = VougeAdapter(database.client, db_name = database.name)
    lims_sample.udf.pop('Sequencing Analysis')

    # WHEN building a mongo sample
    mongo_sample = build_sample(lims_sample, lims, adapter)
    
    # THEN the sample should have been parsed witout app_tag
    assert mongo_sample.get('application_tag') is None


def test_build_sample_wrong_apptag(lims_sample, lims, database):
    # GIVEN a lims sample with missing application tag
    #  and a database with application tags
    database.application_tag.update_one({'_id' : 'WGSPCFC030'}, {'$set' : {"category" : "wgs"}},
                                         upsert=True)

    lims_sample.udf['Sequencing Analysis'] = 'NOTINDATABASE'
    adapter = VougeAdapter(database.client, db_name = database.name)
    lims_sample.udf.pop('Sequencing Analysis')

    # WHEN building a mongo sample
    mongo_sample = build_sample(lims_sample, lims, adapter)
    
    # THEN the sample should have been parsed witout app_tag
    assert mongo_sample.get('application_tag') is None


def test_build_sample_family(family_sample, lims, database):
    # GIVEN a lims sample with a valid application tag
    #  and a database with application tags and a family
    database.application_tag.update_one({'_id' : 'WGSPCFC030'},
                                         {'$set' : {"category" : "wgs"}},
                                         upsert=True)
    family_sample.udf['Sequencing Analysis'] = 'WGSPCFC030'
    adapter = VougeAdapter(database.client, db_name = database.name)

    # WHEN building a mongo sample
    mongo_sample = build_sample(family_sample, lims, adapter)


    # THEN the sample should have been parsed in the correct way
    assert mongo_sample['family'] == family_sample.udf.get('Family')



