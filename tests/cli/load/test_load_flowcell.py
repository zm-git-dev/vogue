from vogue.commands.load.application_tag import application_tags
from vogue.server import create_app
from vogue.commands.base import cli
from vogue.adapter.plugin import VougeAdapter


app = create_app(test= True)


def test_flowcell(database):
    app.db = database
    app.adapter = VougeAdapter(database.client, db_name = database.name)

    ## GIVEN a lims with a process 24-100451, such as:
    
    
    ## WHEN adding a flowcell tags
    runner = app.test_cli_runner()
    result = runner.invoke(cli, ['load', 'flowcell', '-r', '24-100451'])

    ## THEN assert the new flowcell should be added to the colleciton
    assert app.adapter.flowcell(run_id) == {}


