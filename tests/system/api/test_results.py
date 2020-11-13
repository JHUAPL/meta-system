#  **********************************************************************
#  Copyright (C) 2020 Johns Hopkins University Applied Physics Laboratory
#
#  All Rights Reserved.
#  For any other permission, please contact the Legal Office at JHU/APL.
#  **********************************************************************
import json
import os
import unittest

import pandas as pd

from shared.config import config
from system.api.results import get_result_dataframe, build_hierarchy, list_files_for_download


class TestResultsFunctions(unittest.TestCase):
    def setUp(self) -> None:
        self.tsv_result_good = os.path.join(config.TEST_DATA_DIR, "mock_auc.tsv")
        self.tsv_result_good_columns = ["classifier_name", "rank", "L2", "AUPRC"]

        self.tsv_result_no_exist = os.path.join(os.pardir, os.pardir, "data", "fake_name.tsv")

    def test_get_result_dataframe_good(self):
        res = get_result_dataframe(path=self.tsv_result_good, columns=self.tsv_result_good_columns)
        truth = pd.read_csv(self.tsv_result_good, sep="\t", encoding="utf-8", names=self.tsv_result_good_columns)
        self.assertTrue(truth.equals(res))

        res = get_result_dataframe(path=self.tsv_result_good, columns=None)
        truth = pd.read_csv(self.tsv_result_good, sep="\t", encoding="utf-8")
        self.assertTrue(truth.equals(res))
        return

    def test_get_result_dataframe_bad(self):
        res = get_result_dataframe(path=self.tsv_result_no_exist, columns=self.tsv_result_good_columns)
        self.assertEqual(res, None)

        res = get_result_dataframe(path=self.tsv_result_no_exist, columns=None)
        self.assertEqual(res, None)
        return

    def tearDown(self) -> None:
        pass


class TestTaxonomicHierarchy(unittest.TestCase):
    def setUp(self) -> None:
        self.taxid_padded_path = os.path.join(config.TEST_DATA_DIR, "mock_taxid.abu.ts.padded")
        self.taxid_abu_ts_padded_tree = os.path.join(config.TEST_DATA_DIR, "mock_taxid_hierarchy_tree.json")
        self.taxid_abu_ts_df = get_result_dataframe(self.taxid_padded_path, ["taxid", "abundance", "hierarchy"])

    def test_build_hierarchy_good(self):
        hierarchy_col = self.taxid_abu_ts_df["hierarchy"].tolist()
        abundance_col = self.taxid_abu_ts_df["abundance"].tolist()

        tree = build_hierarchy(hierarchy_list=hierarchy_col, abundance_list=abundance_col)

        with open(self.taxid_abu_ts_padded_tree, "r") as f:
            self.assertEqual(tree, json.load(f))
        return

    def tearDown(self) -> None:
        pass


class TestDownloads(unittest.TestCase):
    def setUp(self) -> None:
        self.read_types_1 = ["test_read_type"]
        self.classifiers_1 = ["test_classifier"]
        self.job_id_1 = "5f4936fa3783b2925ad11aac"
        self.files_1 = ["test_read_type/test_classifier/test_classifier.report",
                        "test_read_type/test_classifier/test_classifier.result",
                        "test_read_type/eval/eval.tsv",
                        "test_read_type/eval/classifier_rank_abu_taxid_org_inclusion.tsv",
                        "test_read_type/results/parsed_test_classifier"]

        self.read_types_2 = [""]
        self.classifiers_2 = ["test_classifier"]
        self.job_id_2 = "5ef0cd39e0b6dd1df8c8fdeb"
        self.files_2 = ["test_classifier/test_classifier.report",
                        "test_classifier/test_classifier.result",
                        "eval/classifier_rank_abu_taxid_org_inclusion.tsv",
                        "results/parsed_test_classifier"]
        pass

    def test_list_files_for_download_1(self):
        returned_file_list = list_files_for_download(read_types=self.read_types_1, classifiers=self.classifiers_1,
                                                     job_path=os.path.join(config.TEST_DATA_DIR, "jobs", self.job_id_1))
        self.assertCountEqual(self.files_1, returned_file_list)

    def test_list_files_for_download_2(self):
        returned_file_list = list_files_for_download(read_types=self.read_types_2, classifiers=self.classifiers_2,
                                                     job_path=os.path.join(config.TEST_DATA_DIR, "jobs", self.job_id_2))
        self.assertCountEqual(self.files_2, returned_file_list)

    def tearDown(self) -> None:
        pass


if __name__ == '__main__':
    unittest.main()
