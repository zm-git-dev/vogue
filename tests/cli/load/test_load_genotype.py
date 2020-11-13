from vogue.server import create_app
from vogue.commands.base import cli
from vogue.adapter.plugin import VougeAdapter

app = create_app(test=True)


def test_genotype(database):
    # GIVEN a database and a sample_doc formated in the correct way
    app.db = database
    app.adapter = VougeAdapter(database.client, db_name=database.name)
    sample_id = 'test'
    sample_doc = '{"_id" : "%s" , "sample_created_in_genotype_db" : "2019-11-12" }' % sample_id

    # WHEN running vogue load genotype with that doccument
    runner = app.test_cli_runner()
    result = runner.invoke(cli, ['load', 'genotype', '-s', sample_doc])

    # THEN its added to the database
    added_sample = app.adapter.genotype_analysis_collection.find_one(
        {'_id': sample_id})
    assert app.adapter.genotype_analysis_collection.estimated_document_count(
    ) == 1
    assert added_sample['_id'] == sample_id


def test_genotype_no_id(database):
    # GIVEN a database and a sample_doc formated in the correct way
    app.db = database
    app.adapter = VougeAdapter(database.client, db_name=database.name)
    sample_id = 'test'
    sample_doc = '{"sample_created_in_genotype_db" : "2019-11-12" }'

    # WHEN running vogue load genotype with that doccument
    runner = app.test_cli_runner()
    result = runner.invoke(cli, ['load', 'genotype', '-s', sample_doc])

    # THEN no sample was added
    assert app.adapter.genotype_analysis_collection.estimated_document_count(
    ) == 0


def test_genotype_badly_formated_json(database):
    # GIVEN a database and a badly formated sample_doc
    app.db = database
    app.adapter = VougeAdapter(database.client, db_name=database.name)
    sample_id = 'test'
    sample_doc = '{"bad", "format", 23 "sample_created_in_genotype_db": "2019-09-02", "sex": "fema'

    # WHEN running vogue load genotype with that doccument
    runner = app.test_cli_runner()
    result = runner.invoke(cli, ['load', 'genotype', '-s', sample_doc])

    # THEN assert no sample was added
    assert app.adapter.genotype_analysis_collection.estimated_document_count(
    ) == 0
