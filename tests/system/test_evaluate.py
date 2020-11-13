#  **********************************************************************
#  Copyright (C) 2020 Johns Hopkins University Applied Physics Laboratory
#
#  All Rights Reserved.
#  For any other permission, please contact the Legal Office at JHU/APL.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#  **********************************************************************
import os
import shutil
import unittest

import pydash
import pymongo
from pymodm import connect

from shared.config import config
from system.controllers import user, user_job, evaluation_job
from system.evaluate import evaluate
from system.extensions import DockerClient
from system.models.job_manager import JobStatus, JobMode

docker_client = DockerClient().get_client()

# Set-up mongo database connection
mongo_uri = config.MONGO_URI
my_client = pymongo.MongoClient(mongo_uri)
db_name = "TestMETA"
db = my_client[db_name]
connect(mongo_uri + db_name)  # Connect to MongoDB


class TestEvaluationOfRealReadJob(unittest.TestCase):
    def setUp(self) -> None:
        # Files to check for
        self.important_metacompare_outputs = ["classifier_rank_abu_taxid_org_inclusion.tsv",
                                              os.path.join("tmp", "parsed_mash_dir", "taxid.abu.ts"),
                                              os.path.join("tmp", "parsed_mash_dir", "taxid.abu.ts.padded"),
                                              os.path.join("tmp", "parsed_kraken2_dir", "taxid.abu.ts"),
                                              os.path.join("tmp", "parsed_kraken2_dir", "taxid.abu.ts.padded")]

        # Set-up database documents for evaluation job
        self.classifiers = ["kraken2", "mash"]
        self.user_id = user.insert("Joe Schmo", "Joe.Schmo@hotmail.com", [])
        self.user_job_id = user_job.insert(user_id=self.user_id, title="my job title", read_types=["Z"],
                                           classifiers=self.classifiers, mode=JobMode.REAL_READS)
        self.eval_job_id = evaluation_job.insert(user_job_id=self.user_job_id)
        evaluation_job.update_status(obj_id=self.eval_job_id, new_status=str(JobStatus.QUEUED))
        self.eval_job_data = evaluation_job.find_by_id(eval_job_id=self.eval_job_id).as_dict()

        # Set-up job directory
        self.job_path = os.path.join(config.TEST_DATA_DIR, "jobs", str(self.user_job_id))
        os.makedirs(os.path.join(self.job_path))

        # Copy files into job directory
        src = os.path.join(config.TEST_DATA_DIR, "classifier_outputs")
        dst = self.job_path
        for c in self.classifiers:
            shutil.copytree(os.path.join(src, c), os.path.join(dst, c))
        shutil.copyfile(os.path.join(config.TEST_DATA_DIR, "mock.tsv"), os.path.join(self.job_path, "mock.tsv"))

        # Directories to check for
        self.results_dir = os.path.join(self.job_path, "results")
        os.mkdir(self.results_dir)
        self.eval_dir = os.path.join(self.job_path, "eval")
        os.mkdir(self.eval_dir)

    def test_evaluate_good(self):
        # Function to test
        evaluate(job_dir=self.job_path, classifiers=self.classifiers, eval_job_id=self.eval_job_id,
                 user_job_id=self.user_job_id, job_mode_enum=JobMode.REAL_READS)

        # Check that each classifier creates a parsed file
        for c in self.classifiers:
            classifier_result_path = os.path.join(self.results_dir, "parsed_{}".format(c))
            self.assertTrue(os.path.exists(classifier_result_path))

        # Check metacompare.sh files are generated
        for f in self.important_metacompare_outputs:
            eval_file_path = os.path.join(self.eval_dir, f)
            self.assertTrue(os.path.exists(eval_file_path))

        # Check evaluation job attributes are updated
        eval_job_data = evaluation_job.find_by_id(eval_job_id=self.eval_job_id)
        self.assertIsNotNone(pydash.get(eval_job_data, "cpu_time"))
        self.assertIsNotNone(pydash.get(eval_job_data, "wall_clock_time"))
        self.assertEqual(pydash.get(eval_job_data, "status"), str(JobStatus.COMPLETED))

        # Check user job attributes are updated
        user_job_data = user_job.find_by_id(user_job_id=self.user_job_id)
        self.assertIsNotNone(pydash.get(user_job_data, "completed_datetime"))

    def tearDown(self) -> None:
        shutil.rmtree(os.path.join(config.TEST_DATA_DIR, "jobs", str(self.user_job_id)))
        pass


class TestEvaluationOfSimulationJob(unittest.TestCase):
    def setUp(self) -> None:
        # Files to check for
        self.important_metacompare_outputs = ["classifier_rank_abu_taxid_org_inclusion.tsv",
                                              "eval.tsv",
                                              os.path.join("tmp", "BASELINE1.tsv_dir", "taxid.abu.ts"),
                                              os.path.join("tmp", "BASELINE1.tsv_dir", "taxid.abu.ts.padded"),
                                              os.path.join("tmp", "parsed_mash_dir", "taxid.abu.ts"),
                                              os.path.join("tmp", "parsed_mash_dir", "taxid.abu.ts.padded"),
                                              os.path.join("tmp", "parsed_kraken2_dir", "taxid.abu.ts"),
                                              os.path.join("tmp", "parsed_kraken2_dir", "taxid.abu.ts.padded")]

        # Set-up database documents for evaluation job
        self.classifiers = ["kraken2", "mash"]
        self.read_type = "miseq"
        self.user_id = user.insert("Joe Schmo", "Joe.Schmo@hotmail.com", [])
        self.user_job_id = user_job.insert(user_id=self.user_id, title="my job title", read_types=["Z"],
                                           classifiers=self.classifiers, mode=JobMode.SIMULATED_READS)
        self.eval_job_id = evaluation_job.insert(user_job_id=self.user_job_id, read_type=self.read_type)
        evaluation_job.update_status(obj_id=self.eval_job_id, new_status=str(JobStatus.QUEUED))
        self.eval_job_data = evaluation_job.find_by_id(eval_job_id=self.eval_job_id).as_dict()

        # Set-up job directory
        self.job_path = os.path.join(config.TEST_DATA_DIR, "jobs", str(self.user_job_id))
        self.job_path_with_read_type = os.path.join(self.job_path, self.read_type)
        os.makedirs(os.path.join(self.job_path, self.read_type))

        # Copy files into job directory
        src = os.path.join(config.TEST_DATA_DIR, "classifier_outputs")
        dst = os.path.join(self.job_path, self.read_type)
        for c in self.classifiers:
            shutil.copytree(os.path.join(src, c), os.path.join(dst, c))
        shutil.copyfile(os.path.join(config.TEST_DATA_DIR, "mock.tsv"), os.path.join(self.job_path, "mock.tsv"))

        # Directories to check for
        self.results_dir = os.path.join(self.job_path_with_read_type, "results")
        os.mkdir(self.results_dir)
        self.eval_dir = os.path.join(self.job_path_with_read_type, "eval")
        os.mkdir(self.eval_dir)

    def test_evaluate_good(self):

        # Function to test
        evaluate(job_dir=self.job_path_with_read_type, classifiers=self.classifiers, eval_job_id=self.eval_job_id,
                 user_job_id=self.user_job_id, job_mode_enum=JobMode.SIMULATED_READS)

        # Check that each classifier creates a parsed file
        for c in self.classifiers:
            classifier_result_path = os.path.join(self.results_dir, "parsed_{}".format(c))
            self.assertTrue(os.path.exists(classifier_result_path))

        # Check metacompare.sh files are generated
        for f in self.important_metacompare_outputs:
            eval_file_path = os.path.join(self.eval_dir, f)
            self.assertTrue(os.path.exists(eval_file_path))

        # Check evaluation job attributes are updated
        eval_job_data = evaluation_job.find_by_id(eval_job_id=self.eval_job_id)
        self.assertIsNotNone(pydash.get(eval_job_data, "cpu_time"))
        self.assertIsNotNone(pydash.get(eval_job_data, "wall_clock_time"))
        self.assertEqual(pydash.get(eval_job_data, "status"), str(JobStatus.COMPLETED))

        # Check user job attributes are updated
        user_job_data = user_job.find_by_id(user_job_id=self.user_job_id)
        self.assertIsNotNone(pydash.get(user_job_data, "completed_datetime"))

    def tearDown(self) -> None:
        shutil.rmtree(os.path.join(config.TEST_DATA_DIR, "jobs", str(self.user_job_id)))
        pass
