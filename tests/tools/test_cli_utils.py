import yaml, json
import unittest

from vogue.tools.cli_utils import json_read, yaml_read, check_file, NotAFileError
from vogue.tools.cli_utils import add_doc

INVALID_JSON = 'tests/fixtures/invalid_multiqc.json'
VALID_JSON = 'tests/fixtures/valid_multiqc.json'
INVALID_YAML = 'tests/fixtures/invalid_multiqc.yaml'
VALID_YAML = 'tests/fixtures/valid_multiqc.yaml'
NO_FILE = 'tests/fixtures/no_exist_file.data'
NOT_FILE = 'tests/fixtures'


class TestCase_check_file(unittest.TestCase):

    def test_add_doc(self):
        @add_doc("doc decorator")
        def my_func():
            pass

        self.assertEqual(my_func.__doc__, "doc decorator")
    
    def test_check_file(self):
        with self.assertRaises(NotAFileError) as e:
            check_file(NOT_FILE)

        with self.assertRaises(FileNotFoundError) as e:
            check_file(NO_FILE)

    def test_json_read(self):
        self.assertEqual(json_read(INVALID_JSON), False)
        self.assertIsInstance(json_read(VALID_JSON), dict)

    def test_yaml_read(self):
        self.assertEqual(yaml_read(INVALID_YAML), False)
        self.assertIsInstance(yaml_read(VALID_YAML), dict)
