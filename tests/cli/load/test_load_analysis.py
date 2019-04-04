from vogue.server import create_app
from vogue.commands.base import cli
from vogue.adapter.plugin import VougeAdapter

VALID_JSON = 'tests/fixtures/valid_multiqc.json'

app = create_app(test= True)


def test_analysis(database):
    app.db = database
    app.adapter = VougeAdapter(database.client, db_name = database.name)

    ## GIVEN a correct foramted input file VALID_JSON
    sample_id = 'some_id'
    
    ## WHEN adding a new analysis
    runner = app.test_cli_runner()
    result = runner.invoke(cli, ['load', 'analysis', '-s', sample_id ,'-a', VALID_JSON ,'-t', 'QC' ])

    ## THEN assert the new apptag should be added to the colleciton
    assert isinstance(app.adapter.analysis(sample_id), dict)


def test_analysis_wrong_file(database):
    app.db = database
    app.adapter = VougeAdapter(database.client, db_name = database.name)

    ## GIVEN a invalid path to a json file
    sample_id = 'some_id'
    
    ## WHEN adding a new analysis
    runner = app.test_cli_runner()
    result = runner.invoke(cli, ['load', 'analysis', '-s', sample_id ,'-a', 'path' ,'-t', 'QC' ])

    ## THEN assert  Can not load json. Exiting.
    assert result.exit_code == 1

