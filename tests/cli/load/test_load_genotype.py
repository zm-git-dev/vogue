from vogue.server import create_app
from vogue.commands.base import cli
from vogue.adapter.plugin import VougeAdapter

app = create_app(test= True)

def test_genotype(database, lims):
    # GIVEN a database and a sample_doc formated in the correct way
    app.db = database
    app.adapter = VougeAdapter(database.client, db_name = database.name)
    sample_id = 'test'
    sample_doc = '{"_id" : "%s" , "sample_created_in_genotype_db" : "2019-11-12" }' % sample_id

    # WHEN running vogue load genotype with that doccument
    runner = app.test_cli_runner()
    result = runner.invoke(cli, ['load', 'genotype', '-s', sample_doc])

    # THEN its added to the database
    added_sample = app.adapter.maf_analysis_collection.find_one({'_id': sample_id})
    assert app.adapter.maf_analysis_collection.count() == 1
    assert added_sample['_id'] == sample_id

def test_genotype_no_id(database, lims):
    # GIVEN a database and a sample_doc formated in the correct way
    app.db = database
    app.adapter = VougeAdapter(database.client, db_name = database.name)
    sample_id = 'test'
    sample_doc = '{"sample_created_in_genotype_db" : "2019-11-12" }'

    # WHEN running vogue load genotype with that doccument
    runner = app.test_cli_runner()
    result = runner.invoke(cli, ['load', 'genotype', '-s', sample_doc])

    # THEN no sample was added
    assert app.adapter.maf_analysis_collection.count() == 0