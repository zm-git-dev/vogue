from vogue.load.genotype import load_sample
from vogue.adapter.plugin import VougeAdapter
from vogue.server import create_app
from json.decoder import JSONDecodeError
import pytest	



app = create_app(test= True)

def test_load_sample(database, lims):
    # GIVEN a database and a badly formated json string
    app.db = database
    app.adapter = VougeAdapter(database.client, db_name = database.name)
    genotype_sample_string = '{"bad", "format", 23 "sample_created_in_genotype_db": "2019-09-02", "sex": "female", "snps": {}}'

    # WHEN running load_sample
    # THEN JSONDecodeError is raised
    assert load_sample(app.adapter, genotype_sample_string) is None
