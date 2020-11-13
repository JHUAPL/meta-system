#  **********************************************************************
#  Copyright (C) 2020 Johns Hopkins University Applied Physics Laboratory
#
#  All Rights Reserved.
#  For any other permission, please contact the Legal Office at JHU/APL.
#  **********************************************************************

import os
import unittest

from shared.config import config
from system.utils.biocontainers import get_biocontainers_parser


class TestBiocontainers(unittest.TestCase):
    def setUp(self) -> None:
        BIOCONTAINERS = os.path.join(config.TEST_DATA_DIR, "mock_biocontainers.yaml")
        biocontainers_yaml = open(BIOCONTAINERS, "r")
        self.yaml_file = biocontainers_yaml
        self.foo1_link = "https://foobar.com"

    def test_get_biocontainers_parser(self):
        biocontainers_names, biocontainers_info = get_biocontainers_parser(yaml_file=self.yaml_file)
        self.assertEqual(biocontainers_names, ["foo1", "foo2"])
        self.assertEqual(biocontainers_info["foo1"].link, self.foo1_link)
        return


if __name__ == '_main_':
    unittest.main()
