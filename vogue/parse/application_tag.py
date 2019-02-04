

def parse_application_tag(json_list:list)-> dict:
    """Will convert a json_list with application tags to a dictonary.
    
    Args:
        json_list(list(dict)): [{'tag':'MELPCFR030', 'category':'wgs',...},...]
    Returns: A dict where keys are application tags and values are catehories.
        application_tags(dict): {'MELPCFR030': 'wgs', '':'',...}
    """    
    application_tags = {}
    for app_tag in json_list:
        tag = app_tag.get('tag')
        cat = app_tag.get('category')
        if tag and cat:
            application_tags[tag] = cat
    return application_tags
