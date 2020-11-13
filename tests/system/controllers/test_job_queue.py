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
import unittest

import pymongo
from pymodm import connect

from shared.config import config
from system.controllers import user, user_job, evaluation_job, job_queue, controllers
from system.models.job_manager import JobMode, JobType
from system.models.schemas_loader import SchemaLoader


class TestJobQueueController(unittest.TestCase):
    def setUp(self) -> None:
        self.mongo_uri = config.MONGO_URI
        self.my_client = pymongo.MongoClient(self.mongo_uri)
        self.db_name = "TestMETA"
        self.db = self.my_client[self.db_name]
        connect(self.mongo_uri + self.db_name)  # Connect to MongoDB

        self.user_id = user.insert("Joe Schmo", "Joe.Schmo@hotmail.com", [])
        self.user_job_id = user_job.insert(user_id=self.user_id, title="my job title", read_types=["Z"],
                                           classifiers=["A", "B"], mode=JobMode.REAL_READS)
        self.eval_job_id = evaluation_job.insert(user_job_id=self.user_job_id, read_type="miseq")
        self.job_type = JobType.EVALUATION

        self.queue_id = job_queue.insert(job_type=self.job_type, job_id=self.eval_job_id)

    def test_insert(self):
        queue_id = job_queue.insert(job_type=self.job_type, job_id=self.eval_job_id)
        self.assertIsNotNone(queue_id)

    def test_delete(self):
        pre_queue_size = controllers.count(SchemaLoader.JOB_QUEUE)
        job_queue.delete(obj_id=self.queue_id)
        post_queue_size = controllers.count(SchemaLoader.JOB_QUEUE)
        self.assertEqual(pre_queue_size - 1, post_queue_size)

    def tearDown(self) -> None:
        col_list = self.db.list_collection_names()
        for col in col_list:
            self.db.drop_collection(col)
