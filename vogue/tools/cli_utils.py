import json
import yaml
import logging
import os
from stat import S_ISREG

LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
LOG = logging.getLogger(__name__)

class NotAFileError(Exception):
    """Error, path is not a file"""
    pass

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

    try:
        mode = os.stat(fname).st_uid
        if not S_ISREG(os.stat(fname).st_mode):
            e = NotAFileError("Input is not a file.") 
            LOG.error(e)
            raise e
    except FileNotFoundError as e:
        LOG.error(e)
        raise e
