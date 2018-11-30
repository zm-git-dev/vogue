import json
import yaml
import logging

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
    except json.JSONDecodeError as e:
        #LOG.warning(f"Trying JSON format {e}")
        return e 

def yaml_read(fname):
    """
    Reads YAML file and returns dictionary. Returns error if can't read.
    """

    try:
        with open(fname, 'r') as f:
            analysis_conf = yaml.load(f)
            return analysis_conf
    except (yaml.YAMLError, yaml.scanner.ScannerError) as e:
        #LOG.warning(f"Trying YAML format {e}")
        return e

def check_file(fname):
    """
    Check file exists and readable.
    """

    try:
        with open(fname,'r') as f:
            garbage = f.readlines()
    except (IOError, FileNotFoundError) as e:
        LOG.error(e)
        raise e


