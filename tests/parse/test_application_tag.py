from vogue.parse.application_tag import parse_application_tag

def test_parse_application_tag():
    ## GIVEN a json_list of correct format
    json_list = [{"tag" : "WGSPCFC030", "category" : "wgs"}]

    ## WHEN running parse_application_tag
    application_tags = parse_application_tag(json_list)

    ### THEN it returns a dict where keys are app tags and values are cateories
    assert application_tags == {"WGSPCFC030" : "wgs"}


def test_parse_application_tag_wrong_format():
    ## GIVEN a json_list of wrong format
    json_list = [{"tae" : "WGSPCFC030", "categor" : "wgs"}]

    ## WHEN running parse_application_tag
    application_tags = parse_application_tag(json_list)

    ### THEN the tag is not added
    assert application_tags.get("WGSPCFC030") is None