from vogue.adapter.plugin import VougeAdapter
from vogue.load.sample import update_category
import pytest
from vogue.exceptions import MissingApplicationTag	


def test_update_category(database):
    ## GIVEN a json_list and a database with a sample with a valid app tag
    json_list = [{"tag" : "WGSPCFC030", "category" : "wgs"}]
    database.sample.update_one({'_id' : 'test'}, 
                            {'$set': {'application_tag' : 'WGSPCFC030'}}, 
                            upsert=True) 
    adapter = VougeAdapter(database.client, db_name = database.name)

    ## WHEN running update_category
    update_category(adapter, json_list)

    ### THEN the app tags should be added 
    assert adapter.sample('test')['category'] == 'wgs'


def test_update_category_wrong_tag(database):
    ## GIVEN a json_list and a database with a sample with a non valid app tag
    json_list = [{"tag" : "WGSPCFC030", "category" : "wgs"}]
    database.sample.update_one({'_id' : 'test'}, 
                            {'$set': {'application_tag' : 'WRONGTAG'}}, 
                            upsert=True) 
    adapter = VougeAdapter(database.client, db_name = database.name)

    ## WHEN running update_category
    update_category(adapter, json_list) 

    ## THEN the 
    assert adapter.sample('test').get('category') is None