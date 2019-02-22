
from vogue.commands.load.application_tag import application_tags
from vogue.server import create_app
from vogue.commands.base import cli
import pytest
from click import Abort
from vogue.adapter.plugin import VougeAdapter


app = create_app(test= True)


def test_application_tag(database):
    app.db = database
    app.adapter = VougeAdapter(database.client, db_name = database.name)

    ## GIVEN a correct foramted input string
    app_tags = '[{"tag":"MELPCFR030", "category":"wgs"}]'
    
    ## WHEN adding a application tags
    runner = app.test_cli_runner()
    result = runner.invoke(cli, ['load', 'apptag', app_tags])

    ## THEN assert the new apptag should be added to the colleciton
    assert app.adapter.app_tag('MELPCFR030')['category'] == 'wgs'


def test_application_tag_wrong_input(database):
    app.db = database

    ## GIVEN a badly foramted input string
    app_tags = "[{'tag':'MELPCFR030', 'category':'wgs'}]}"

    ## WHEN adding a application tags
    runner = app.test_cli_runner()
    result = runner.invoke(cli, ['load', 'apptag', app_tags])

    ## THEN assert Badly formated json! Can not load json. Exiting. 
    assert result.exit_code == 1
