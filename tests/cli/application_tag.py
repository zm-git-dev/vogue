from vogue.commands.load.application_tag import application_tags
import pytest



def test_application_tag(invoke_cli):
    ## GIVEN a correct foramted input string
    app_tags = "[{'tag':'MELPCFR030', 'category':'wgs'}]"

    ## WHEN adding a application tags
    invoke_cli(['load', 'apptag', '-a', app_tags])

    ## THEN assert okidoki



def test_application_tag_wrong_input(invoke_cli):
    ## GIVEN a badly foramted input string
    app_tags = "[{'tag':'MELPCFR030', 'category':'wgs'}]}"

    ## WHEN adding a application tags
    ## THEN assert error
    with pytest.raises(ValueError):
        invoke_cli(['load', 'apptag', '-a', app_tags])