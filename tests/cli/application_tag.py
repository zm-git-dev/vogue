from vogue.commands.load.application_tag import application_tags
import pytest




def test_application_tag(database, invoke_cli):
    ## GIVEN a correct foramted input string
    app_tags = '[{"tag":"ABCD", "category":"wgs"}]'


    result =  invoke_cli(['load', '-d',  'apptag', '-a', app_tags])
    assert result.exit_code == 0

    # check that the server was added to the "nodes" collection
    assert database['nodes'].find().count() == 1


#def test_application_tag(adapter, invoke_cli):
    ## GIVEN a correct foramted input string
   # app_tags = '[{"tag":"ABCD", "category":"wgs"}]'

    ## WHEN adding a application tags
    #print('hej')
    #invoke_cli(['load', 'apptag', '-a', app_tags])

    ## THEN assert okidoki
    #assert adapter
    #assert adapter.app_tag_collection.find_one("MELPCFR030")



#def test_application_tag_wrong_input(invoke_cli):
    ## GIVEN a badly foramted input string
#    app_tags = "[{'tag':'MELPCFR030', 'category':'wgs'}]}"

    ## WHEN adding a application tags
    ## THEN assert error
#    with pytest.raises(ValueError):
#        invoke_cli(['load', '-d', 'trending_stage', 'apptag', '-a', app_tags])