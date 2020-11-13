#  **********************************************************************
#  Copyright (C) 2020 Johns Hopkins University Applied Physics Laboratory
#
#  All Rights Reserved.
#  For any other permission, please contact the Legal Office at JHU/APL.
#  **********************************************************************

import os
import unittest

from shared.config import config
from system.utils.zip import send_to_zip


class TestSendToZip(unittest.TestCase):
    def setUp(self) -> None:
        self.user_job_id = "5f4936fa3783b2925ad11aac"
        self.base_path = os.path.join(config.TEST_DATA_DIR, "jobs", self.user_job_id)
        self.list_of_files = [os.path.join("test_read_type", "test_classifier", "test_classifier.report"),
                              os.path.join("test_read_type", "test_classifier", "test_classifier.result"),
                              os.path.join("test_read_type", "eval", "eval.tsv"),
                              os.path.join("test_read_type", "eval", "classifier_rank_abu_taxid_org_inclusion.tsv"),
                              os.path.join("test_read_type", "results", "parsed_test_classifier")]
        self.list_of_files_dne = [os.path.join("foo", "bar", "does_not_exist.report"),
                                  os.path.join("test_read_type", "test_classifier", "test_classifier.result")]

        self.zip_filename = "outfile_test.zip"
        self.zip_filepath = os.path.join(self.base_path, self.zip_filename)

        self.zip_filename_dne = "outfile_test_dne.zip"
        self.zip_filepath_dne = os.path.join(self.base_path, self.zip_filename_dne)

        self.error = False
        pass

    def test_send_to_zip(self):
        res_output = send_to_zip(base_path=self.base_path, list_of_files=self.list_of_files, outfile=self.zip_filename)
        self.assertEqual(res_output, True)
        self.assertEqual(os.path.exists(self.zip_filepath), True)
        return

    def test_send_to_zip_dne(self):
        res_output = send_to_zip(base_path=self.base_path, list_of_files=self.list_of_files_dne,
                                 outfile=self.zip_filename_dne)
        self.assertEqual(res_output, True)
        self.assertEqual(os.path.exists(self.zip_filepath_dne), True)
        return

    def tearDown(self) -> None:
        if os.path.exists(self.zip_filepath):
            os.remove(self.zip_filepath)
        if os.path.exists(self.zip_filepath_dne):
            os.remove(self.zip_filepath_dne)
