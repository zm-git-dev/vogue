import json
import yaml
import logging
import os
import pathlib

LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
LOG = logging.getLogger(__name__)

def add_doc(docstring):
    """
    A decorator for adding docstring. Taken shamelessly from stackexchange.
    """

    def document(func):
        func.__doc__ = docstring
        return func

    return document

def json_read(fname):
    """
    Reads JSON file and returns dictionary. Returns error if can't read.
    """

    try:
        with open(fname, 'r') as f:
            analysis_conf = json.load(f)
            return analysis_conf
    except:
        LOG.warning('Input config is not JSON')
        return False 

def yaml_read(fname):
    """
    Reads YAML file and returns dictionary. Returns error if can't read.
    """

    try:
        with open(fname, 'r') as f:
            analysis_conf = yaml.load(f)
            return analysis_conf
    except:
        LOG.warning('Input config is not YAML')
        return False

def check_file(fname):
    """
    Check file exists and readable.
    """

    path = pathlib.Path(fname)

    if not path.exists() or not path.is_file():
        LOG.error("File not found or input is not a file.")
        raise FileNotFoundError

def concat_dict_keys(my_dict: dict, key_name="", out_key_list=list()):
    '''
    Recursively create a list of key:key1,key2 from a nested dictionary
    '''

    if isinstance(my_dict, dict):

        if key_name != "":
            out_key_list.append(key_name + ":" +
                                ", ".join(list(my_dict.keys())))

        for k in my_dict.keys():
            concat_dict_keys(my_dict[k], key_name=k, out_key_list=out_key_list)

    return out_key_list
