import yaml
import json
import unittest
import logging

from vogue.tools.cli_utils import json_read
from vogue.tools.cli_utils import yaml_read
from vogue.tools.cli_utils import check_file
from vogue.build.analysis import validate_conf
from vogue.build.analysis import build_analysis

INVALID_JSON = 'tests/fixtures/not_a_multiqc_report.json'
VALID_JSON = 'tests/fixtures/valid_multiqc.json'
NO_FILE = 'tests/fixtures/no_exist_file.data'
NOT_FILE = 'tests/fixtures'


class Testcase_analysis(unittest.TestCase):
    def test_validate_conf(self):

        invalid_analysis_dict = json_read(INVALID_JSON)
        self.assertEqual(validate_conf(invalid_analysis_dict), False)

        valid_analysis_dict = json_read(VALID_JSON)
        self.assertEqual(validate_conf(valid_analysis_dict), True)

    def test_build_analysis(self):

        valid_analysis_dict = json_read(VALID_JSON)

        analysis_type = 'QC'
        ready_analysis_dict = build_analysis(valid_analysis_dict,
                                             analysis_type)

        self.assertIsInstance(ready_analysis_dict, dict)
        
        analysis_type = 'something_else'
        ready_analysis_dict = build_analysis(valid_analysis_dict,
                                             analysis_type)
        self.assertIsNone(ready_analysis_dict, None)
