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
from system.controllers import user, user_job
from system.models.job_manager import JobMode


class TestClassificationJobController(unittest.TestCase):
    def setUp(self) -> None:
        self.mongo_uri = config.MONGO_URI
        self.my_client = pymongo.MongoClient(self.mongo_uri)
        self.db_name = "TestMETA"
        self.db = self.my_client[self.db_name]
        connect(self.mongo_uri + self.db_name)  # Connect to MongoDB

        self.user_id = user.insert("Joe Schmo", "Joe.Schmo@hotmail.com", [])

    def test_insert(self):
        user_id = user.insert("Joe Schmo", "Joe.Schmo@hotmail.com", [])
        self.assertIsNotNone(user_id)

    def test_find_all_user_jobs(self):
        user_job.insert(user_id=self.user_id, title="my job title 1", read_types=["Z"], classifiers=["A", "B"],
                        mode=JobMode.REAL_READS)
        user_job.insert(user_id=self.user_id, title="my job title 2", read_types=["Z"], classifiers=["A", "B"],
                        mode=JobMode.REAL_READS)
        user_job.insert(user_id=self.user_id, title="my job title 3", read_types=["Z"], classifiers=["A", "B"],
                        mode=JobMode.REAL_READS)
        data = user.find_all_user_jobs(user_id=self.user_id)
        self.assertEqual(len(data), 3)

    def tearDown(self) -> None:
        col_list = self.db.list_collection_names()
        for col in col_list:
            self.db.drop_collection(col)
