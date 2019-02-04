from vogue.build.application_tag import build_application_tag


def test_build_application_tag():
    ## GIVEN a app_tag with missing requiered keys 'tag' and 'category'
    app_tag = {'tag':'MELPCFR030', 'category':'wgs', 'gunnar': 25}

    ## WHEN building a mongo application tag
    mongo_application_tag = build_application_tag(app_tag)

    ## THEN assert mongo_application_tag is {'_id':'MELPCFR030', 'category':'wgs'}
    assert mongo_application_tag ==  {'_id':'MELPCFR030', 'category':'wgs'}


def test_build_application_tag_wrong_input():
    ## GIVEN a app_tag with missing requiered keys 'tag' and 'category'
    app_tag = {'tage':'ABC', 'categoryy':'wgs', 'gunnar': 25}

    ## WHEN building a mongo application tag
    try:
        mongo_application_tag = build_application_tag(app_tag)
    except MissingApplicationTag:
        LOG.warning('ApplicationTag missing in JSON list')

    ## THEN assert mongo_application_tag is None
    assert mongo_application_tag is None

