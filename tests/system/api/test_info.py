#  **********************************************************************
#  Copyright (C) 2020 Johns Hopkins University Applied Physics Laboratory
#
#  All Rights Reserved.
#  For any other permission, please contact the Legal Office at JHU/APL.
#  **********************************************************************

import os
import unittest

from shared.config import config
from system.api.info import get_classifiers_links, get_classifiers_name, get_read_types_links, get_read_type_names
from system.utils.biocontainers import get_biocontainers_parser
from system.utils.readtypes import get_read_types_parser


class TestInfoRetrieval(unittest.TestCase):
    def setUp(self):
        BIOCONTAINERS = os.path.join(config.TEST_DATA_DIR, "mock_biocontainers.yaml")
        READ_TYPES = os.path.join(config.TEST_DATA_DIR, "mock_read_types.yaml")
        biocontainers_yaml = open(BIOCONTAINERS, "r")
        read_types_yaml = open(READ_TYPES, "r")
        self.biocontainer_names, self.biocontainer_info = get_biocontainers_parser(yaml_file=biocontainers_yaml)
        self.read_types_names, self.read_types_info = get_read_types_parser(yaml_file=read_types_yaml)
        pass

    def test_get_classifiers_links(self):
        res = get_classifiers_links(classifier_info=self.biocontainer_info)
        truth = [{"name": "foo1", "link": "https://foobar.com"}, {"name": "foo2", "link": "https://foobar.com"}]
        self.assertEqual(res, truth)
        return

    def test_get_classifiers_name(self):
        res = get_classifiers_name(classifier_names=self.biocontainer_names)
        truth = {"data": ["foo1", "foo2"]}
        self.assertEqual(res, truth)
        return

    def test_get_read_types_links(self):
        res = get_read_types_links(read_types_info=self.read_types_info)
        truth = [{"name": "abc", "prodlink": "https://foo.com", "simlink": "https://foosim.com"}]
        self.assertEqual(res, truth)
        return

    def test_get_read_type_names(self):
        res = get_read_type_names(read_type_names=self.read_types_names)
        truth = {"data": ["abc"]}
        self.assertEqual(res, truth)
        return

    def tearDown(self):
        pass


if __name__ == '_main_':
    unittest.main()
