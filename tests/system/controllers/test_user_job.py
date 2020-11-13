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
from datetime import datetime

import pydash
import pymongo
from bson import ObjectId
from pymodm import connect

from shared.config import config
from system.api.jobs import delete
from system.controllers import user, user_job, classification_job, simulation_job, evaluation_job
from system.models.job_manager import JobMode, JobType, JobStatus


class TestUserJobController(unittest.TestCase):
    def setUp(self) -> None:
        self.mongo_uri = config.MONGO_URI
        self.my_client = pymongo.MongoClient(self.mongo_uri)
        self.db_name = "TestMETA"
        self.db = self.my_client[self.db_name]
        connect(self.mongo_uri + self.db_name)  # Connect to MongoDB

        self.user_id = user.insert("Joe Schmo", "Joe.Schmo@hotmail.com", [])
        self.user_job_id = user_job.insert(user_id=self.user_id, title="my job title", read_types=["Z"],
                                           classifiers=["A", "B"], mode=JobMode.REAL_READS)

        self.obj_id = "5f48522602fb0b2df9058fbd"
        self.job_currently_being_run = True

    def test_insert(self):
        user_job_id = user_job.insert(user_id=self.user_id, title="my job title", read_types=["Z"],
                                      classifiers=["A", "B"], mode=JobMode.REAL_READS)
        self.assertIsNotNone(user_job_id)

        user_job_id = user_job.insert(user_id=self.user_id, title="my job title", read_types=None,
                                      classifiers=["A", "B"], mode=JobMode.REAL_READS)
        self.assertIsNotNone(user_job_id)

    def test_find_all(self):
        data = user_job.find_all()
        self.assertIsNotNone(data)

    def test_find_unhidden_jobs(self):
        user_job.hide_job(obj_id=self.user_id)
        data = user_job.find_unhidden_jobs()
        self.assertIsNotNone(data)

    def test_find_hidden_jobs(self):
        user_job.hide_job(obj_id=self.user_id)
        data = user_job.find_hidden_jobs()
        self.assertIsNotNone(data)

    def test_find_by_id(self):
        data = user_job.find_by_id(user_job_id=self.user_job_id)
        self.assertIsNotNone(data)

    def test_add_child(self):
        child_id = classification_job.insert(user_job_id=self.user_job_id, classifier="kraken", fastq_path="file.fastq")
        prev_num_child, num_child = user_job.add_child(obj_id=self.user_job_id, child_id=child_id,
                                                       job_type=JobType.CLASSIFICATION)
        self.assertEqual(prev_num_child, 0)
        self.assertEqual(num_child, 1)

        child_id = classification_job.insert(user_job_id=self.user_job_id, classifier="kraken2",
                                             fastq_path="file.fastq")
        prev_num_child, num_child = user_job.add_child(obj_id=self.user_job_id, child_id=child_id,
                                                       job_type=JobType.CLASSIFICATION)
        self.assertEqual(prev_num_child, 1)
        self.assertEqual(num_child, 2)

    def test_remove_child_1(self):
        child_id_1 = classification_job.insert(user_job_id=self.user_job_id, classifier="kraken",
                                               fastq_path="file.fastq")
        user_job.add_child(obj_id=self.user_job_id, child_id=child_id_1, job_type=JobType.CLASSIFICATION)
        user_job.remove_child(obj_id=self.user_job_id, child_id=child_id_1, job_type=JobType.CLASSIFICATION)
        data = user_job.find_by_id(user_job_id=self.user_job_id)
        self.assertEqual(len(pydash.get(data, "queue")), 0)
        self.assertEqual(pydash.get(data, "child_jobs_completed"), 1)
        self.assertEqual(pydash.get(data, "status"), str(JobStatus.COMPLETED))

        child_id_2 = classification_job.insert(user_job_id=self.user_job_id, classifier="kraken",
                                               fastq_path="file.fastq")
        user_job.add_child(obj_id=self.user_job_id, child_id=child_id_1, job_type=JobType.CLASSIFICATION)
        user_job.add_child(obj_id=self.user_job_id, child_id=child_id_2, job_type=JobType.CLASSIFICATION)
        user_job.remove_child(obj_id=self.user_job_id, child_id=child_id_1, job_type=JobType.CLASSIFICATION)
        data = user_job.find_by_id(user_job_id=self.user_job_id)
        self.assertEqual(len(pydash.get(data, "queue")), 1)
        self.assertEqual(pydash.get(data, "child_jobs_completed"), 2)
        self.assertEqual(pydash.get(data, "status"), str(JobStatus.COMPLETED))
        # FIXME: assumes if you're removing a child job, the user job is considered COMPLETED?

    def test_update_status(self):
        user_job.update_status(obj_id=self.user_job_id, new_status=str(JobStatus.QUEUED))
        data = user_job.find_by_id(user_job_id=self.user_job_id)
        res = pydash.get(data, "status")
        self.assertEqual(res, str(JobStatus.QUEUED))

    def test_update_queue(self):
        child_id_1 = classification_job.insert(user_job_id=self.user_job_id, classifier="kraken",
                                               fastq_path="file.fastq")
        child_id_2 = classification_job.insert(user_job_id=self.user_job_id, classifier="kraken",
                                               fastq_path="file.fastq")
        queue = [child_id_1, child_id_2]
        user_job.update_queue(obj_id=self.user_job_id, queue_val=queue)
        data = user_job.find_by_id(user_job_id=self.user_job_id)
        res = pydash.get(data, "queue")
        self.assertEqual(res, queue)

    def test_update_abundance_tsv(self):
        user_job.update_abundance_tsv(obj_id=self.user_job_id, abundance_tsv="foo.tsv")
        data = user_job.find_by_id(user_job_id=self.user_job_id)
        self.assertEqual(pydash.get(data, "abundance_tsv"), "foo.tsv")

    def test_update_completion_time(self):
        user_job.update_completion_time(obj_id=self.user_job_id, time=datetime(2020, 5, 19))
        data = user_job.find_by_id(user_job_id=self.user_job_id)
        self.assertEqual(pydash.get(data, "completed_datetime"), datetime(2020, 5, 19))

    def test_update_fastq(self):
        user_job.update_fastq(obj_id=self.user_job_id, fastq="bar.fastq")
        data = user_job.find_by_id(user_job_id=self.user_job_id)
        self.assertEqual(pydash.get(data, "fastq"), "bar.fastq")

    def test_hide_job(self):
        user_job.hide_job(obj_id=self.user_job_id)
        data = user_job.find_by_id(user_job_id=self.user_job_id)
        self.assertEqual(pydash.get(data, "hide"), True)

    def test_unhide_job(self):
        user_job.unhide_job(obj_id=self.user_job_id)
        data = user_job.find_by_id(user_job_id=self.user_job_id)
        self.assertEqual(pydash.get(data, "hide"), False)

    def test_cancel_job_classification(self):
        container_id = "8cd216ad9b38"
        user_job.update_status(obj_id=self.user_job_id, new_status=str(JobStatus.PROCESSING))

        # ----- SET-UP JOB QUEUE -----
        # Queue: [Simulate (COMPLETED), Classify (PROCESSING), Classify (QUEUED), Eval (QUEUED)]
        sim_job_id = simulation_job.insert(user_job_id=self.user_job_id, read_type="iseq", abundance_tsv="foo.tsv",
                                           number_of_reads=5000)
        simulation_job.update_status(obj_id=sim_job_id, new_status=str(JobStatus.COMPLETED))

        class_job_id_1 = classification_job.insert(user_job_id=self.user_job_id, classifier="kraken",
                                                   fastq_path="file.fastq")
        classification_job.update_status(obj_id=class_job_id_1, new_status=str(JobStatus.PROCESSING))
        classification_job.update_container_id(obj_id=class_job_id_1, container_id=container_id)

        class_job_id_2 = classification_job.insert(user_job_id=self.user_job_id, classifier="kraken2",
                                                   fastq_path="file.fastq")
        eval_job_id = evaluation_job.insert(user_job_id=self.user_job_id, read_type="miseq")

        user_job.update_queue(obj_id=self.user_job_id, queue_val=[
            (class_job_id_1, str(JobType.CLASSIFICATION)),
            (class_job_id_2, str(JobType.CLASSIFICATION)),
            (eval_job_id, str(JobType.EVALUATION))
        ])
        # -----------------------------

        job_in_progress, returned_container_id = user_job.cancel_job(obj_id=self.user_job_id)

        user_job_data = user_job.find_by_id(user_job_id=self.user_job_id)
        sim_job_data = simulation_job.find_by_id(sim_job_id=sim_job_id)
        class_job_data_1 = classification_job.find_by_id(class_job_id=class_job_id_1)
        class_job_data_2 = classification_job.find_by_id(class_job_id=class_job_id_2)
        eval_job_data = evaluation_job.find_by_id(eval_job_id=eval_job_id)

        # Check all child job statuses have been set to CANCELLED
        field = "status"
        self.assertEqual(pydash.get(sim_job_data, field), str(JobStatus.COMPLETED))
        self.assertEqual(pydash.get(class_job_data_1, field), str(JobStatus.CANCELLED))
        self.assertEqual(pydash.get(class_job_data_2, field), str(JobStatus.CANCELLED))
        self.assertEqual(pydash.get(eval_job_data, field), str(JobStatus.CANCELLED))

        # Check that all child job container IDs are set to None
        field = "container_id"
        self.assertEqual(pydash.get(sim_job_data, field), None)
        self.assertEqual(pydash.get(class_job_data_1, field), None)
        self.assertEqual(pydash.get(class_job_data_2, field), None)
        self.assertEqual(pydash.get(eval_job_data, field), None)

        # Check that the returned container id is the same as above
        self.assertEqual(returned_container_id, container_id)

        # Check that it set job in progress to True
        self.assertEqual(job_in_progress, True)

        # Check that User Job is set to CANCELLED
        self.assertEqual(pydash.get(user_job_data, "status"), str(JobStatus.CANCELLED))

    def test_cancel_job_simulation(self):
        container_id = "8cd216ad9b38"
        user_job.update_status(obj_id=self.user_job_id, new_status=str(JobStatus.PROCESSING))

        # ----- SET-UP JOB QUEUE -----
        # Queue: [Simulate (PROCESSING), Classify (QUEUED), Classify (QUEUED), Eval (QUEUED)]
        sim_job_id = simulation_job.insert(user_job_id=self.user_job_id, read_type="iseq", abundance_tsv="foo.tsv",
                                           number_of_reads=5000)
        simulation_job.update_status(obj_id=sim_job_id, new_status=str(JobStatus.PROCESSING))
        simulation_job.update_container_id(obj_id=sim_job_id, container_id=container_id)

        class_job_id_1 = classification_job.insert(user_job_id=self.user_job_id, classifier="kraken",
                                                   fastq_path="file.fastq")
        class_job_id_2 = classification_job.insert(user_job_id=self.user_job_id, classifier="kraken2",
                                                   fastq_path="file.fastq")
        eval_job_id = evaluation_job.insert(user_job_id=self.user_job_id, read_type="miseq")

        user_job.update_queue(obj_id=self.user_job_id, queue_val=[
            (sim_job_id, str(JobType.SIMULATION)),
            (class_job_id_1, str(JobType.CLASSIFICATION)),
            (class_job_id_2, str(JobType.CLASSIFICATION)),
            (eval_job_id, str(JobType.EVALUATION))
        ])
        # -----------------------------

        job_in_progress, returned_container_id = user_job.cancel_job(obj_id=self.user_job_id)

        user_job_data = user_job.find_by_id(user_job_id=self.user_job_id)
        sim_job_data = simulation_job.find_by_id(sim_job_id=sim_job_id)
        class_job_data_1 = classification_job.find_by_id(class_job_id=class_job_id_1)
        class_job_data_2 = classification_job.find_by_id(class_job_id=class_job_id_2)
        eval_job_data = evaluation_job.find_by_id(eval_job_id=eval_job_id)

        # Check all child job statuses have been set to CANCELLED
        field = "status"
        self.assertEqual(pydash.get(sim_job_data, field), str(JobStatus.CANCELLED))
        self.assertEqual(pydash.get(class_job_data_1, field), str(JobStatus.CANCELLED))
        self.assertEqual(pydash.get(class_job_data_2, field), str(JobStatus.CANCELLED))
        self.assertEqual(pydash.get(eval_job_data, field), str(JobStatus.CANCELLED))

        # Check that all child job container IDs are set to None
        field = "container_id"
        self.assertEqual(pydash.get(sim_job_data, field), None)
        self.assertEqual(pydash.get(class_job_data_1, field), None)
        self.assertEqual(pydash.get(class_job_data_2, field), None)
        self.assertEqual(pydash.get(eval_job_data, field), None)

        # Check that the returned container id is the same as above
        self.assertEqual(returned_container_id, container_id)

        # Check that it set job in progress to True
        self.assertEqual(job_in_progress, True)

        # Check that User Job is set to CANCELLED
        self.assertEqual(pydash.get(user_job_data, "status"), str(JobStatus.CANCELLED))

    def tearDown(self) -> None:
        col_list = self.db.list_collection_names()
        for col in col_list:
            self.db.drop_collection(col)

class TestDeleteJob(unittest.TestCase):
    def setUp(self) -> None:
        self.user_id = user.insert(name="Username", email="Username@biology.org",
                                    user_jobs=[])
        self.user_job_id_good = user_job.insert(user_id=self.user_id, title="User_Job_Test_Successful",
                                           read_types=["r9"], classifiers=["kraken"], mode=JobMode.SIMULATED_READS)
        self.user_job_id_bad = user_job.insert(user_id=self.user_id, title="User_Job_Test_Unsuccessful",
                                           read_types=["r9"], classifiers=["kraken"], mode=JobMode.SIMULATED_READS)
        self.user_job_id_failed = ObjectId("5f44acd755b9f1ed088fa7f6")

        if not os.path.exists(os.path.join(config.JOBS_DIR, str(self.user_job_id_good))):
            os.mkdir(os.path.join(config.JOBS_DIR, str(self.user_job_id_good)))

        self.delete_successful = "SUCCESSFULLY DELETED JOB {}".format(self.user_job_id_good)
        self.delete_unsucessful = "UNSUCCESSFULLY DELETED JOB {}".format(self.user_job_id_bad)
        self.delete_failed_request = "DELETE JOB {} REQUEST FAILED".format(self.user_job_id_failed)

    def test_delete_jobs(self):
        deletion_message_good = delete(self.user_job_id_good)
        deletion_message_bad = delete(self.user_job_id_bad)
        deletion_message_failed = delete(self.user_job_id_failed)
        self.assertEqual(deletion_message_good[0], self.delete_successful)
        self.assertEqual(deletion_message_bad[0], self.delete_unsucessful)
        self.assertEqual(deletion_message_failed[0], self.delete_failed_request)

    def tearDown(self):
        if os.path.exists(os.path.join(config.JOBS_DIR, str(self.user_job_id_good))):
            shutil.rmtree(os.path.join(config.JOBS_DIR, str(self.user_job_id_good)), ignore_errors=True)


if __name__ == '_main_':
    unittest.main()
