from vogue.exceptions import MissingApplicationTag


def build_application_tag(app_tag: dict) -> dict:
    """Builds the application tag collection documents.
    
    Args: 
        app_tag(dict): {'tag':'MELPCFR030', 'category':'wgs',...}
    Return:
        mongo_application_tag(dict): {'_id':'MELPCFR030', 'category':'wgs'} """

    tag = app_tag.get('tag')
    category = app_tag.get('prep_category')

    if not tag:
        raise MissingApplicationTag

    mongo_application_tag = {'_id': tag}
    if category:
        mongo_application_tag['category'] = category

    return mongo_application_tag
