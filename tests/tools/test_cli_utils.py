import yaml, json
import unittest
import logging

from vogue.tools.cli_utils import json_read, yaml_read, check_file
from vogue.tools.cli_utils import add_doc

INVALID_JSON = 'tests/fixtures/invalid_multiqc.json'
VALID_JSON = 'tests/fixtures/valid_multiqc.json'
INVALID_YAML = 'tests/fixtures/invalid_multiqc.yaml'
VALID_YAML = 'tests/fixtures/valid_multiqc.yaml'
NO_FILE = 'tests/fixtures/no_exist_file.data'
NOT_FILE = 'tests/fixtures'


class Testcase_cli_utils(unittest.TestCase):

    def test_add_doc(self):
        @add_doc("doc decorator")
        def my_func():
            pass

        self.assertEqual(my_func.__doc__, "doc decorator")
    
    def test_check_file(self):
        with self.assertRaises(FileNotFoundError) as e:
            check_file(NOT_FILE)

        with self.assertRaises(FileNotFoundError) as e:
            check_file(NO_FILE)

    def test_json_read(self):
        self.assertEqual(json_read(INVALID_JSON), False)

        self.assertIsInstance(json_read(VALID_JSON), dict)

        with self.assertLogs('json_read', level='WARNING') as l:
            logging.getLogger('json_read').warning('Input config is not JSON')
        self.assertEqual(l.output, ['WARNING:json_read:Input config is not JSON'])

    def test_yaml_read(self):
        self.assertEqual(yaml_read(INVALID_YAML), False)

        self.assertIsInstance(yaml_read(VALID_YAML), dict)

        with self.assertLogs('yaml_read', level='WARNING') as l:
            logging.getLogger('yaml_read').warning('Input config is not YAML')
        self.assertEqual(l.output, ['WARNING:yaml_read:Input config is not YAML'])
