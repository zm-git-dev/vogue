from vogue.commands.load.application_tag import application_tags
from vogue.server import create_app
from vogue.commands.base import cli
from vogue.adapter.plugin import VougeAdapter

app = create_app(test=True)


def test_application_tag(database):
    app.db = database
    app.adapter = VougeAdapter(database.client, db_name=database.name)

    # GIVEN a correct foramted input string
    app_tags = '[{"tag":"MELPCFR030", "prep_category":"wgs"}, {"tag":"MELPCFR090", "prep_category":"hej"}]'

    # WHEN adding a application tags
    runner = app.test_cli_runner()
    result = runner.invoke(cli, ['load', 'apptag', app_tags])

    # THEN assert the new apptags should be added to the colleciton
    assert app.adapter.app_tag_collection.estimated_document_count() == 2
    assert app.adapter.app_tag('MELPCFR030')['category'] == 'wgs'
    assert app.adapter.app_tag('MELPCFR090')['category'] == 'hej'


def test_application_tag_missing_tag(database):
    app.db = database
    app.adapter = VougeAdapter(database.client, db_name=database.name)

    # GIVEN a a input where the tag key is missing for one of the application tag dicts
    app_tags = '[{"category":"wgs"}, {"tag":"MELPCFR030", "category":"wgs"}]'

    # WHEN adding a application tags
    runner = app.test_cli_runner()
    result = runner.invoke(cli, ['load', 'apptag', app_tags])

    # THEN assert the new apptag should be added to the colleciton
    assert app.adapter.app_tag_collection.estimated_document_count() == 1


def test_application_tag_wrong_input(database):
    app.db = database

    # GIVEN a badly foramted input string
    app_tags = "[{'tag':'MELPCFR030', 'category':'wgs'}]}"

    # WHEN adding a application tags
    runner = app.test_cli_runner()
    result = runner.invoke(cli, ['load', 'apptag', app_tags])

    # THEN assert Badly formated json! Can not load json. Exiting.
    assert result.exit_code == 1
