from vogue.commands.load.application_tag import application_tags
from vogue.server import create_app
from vogue.commands.base import cli
from vogue.adapter.plugin import VougeAdapter


app = create_app(test= True)


def test_flowcell(database):
    ## GIVEN a app context with no lims connection 
    app.db = database
    app.adapter = VougeAdapter(database.client, db_name = database.name)

    ## WHEN adding a flowcell tags
    runner = app.test_cli_runner()
    result = runner.invoke(cli, ['load', 'flowcell', '-r', '24-100451'])

    ## THEN assert abort
    assert app.adapter.flowcell(run_id) =


