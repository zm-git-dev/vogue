import logging
LOG = logging.getLogger(__name__)

def build_application_tag(app_tag: dict)-> dict:
    """Builds the application tag collection documents."""

    tag = app_tag.get('tag')
    category = app_tag.get('category')

    if not tag:
        return None

    mongo_application_tag = {'_id' : tag}
    if category:
        mongo_application_tag['category'] = category

    return mongo_application_tag

