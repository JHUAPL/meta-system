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
from collections import namedtuple

import pydash
import pymongo
from bson import ObjectId
from pymodm import connect

from shared.config import config
from system.classify import classify
from system.controllers import classification_job, user, user_job
from system.extensions import DockerClient
from system.models.job_manager import JobStatus, JobMode
from system.utils.biocontainers import get_biocontainers_parser

docker_client = DockerClient().get_client()

# Set-up mongo database connection
mongo_uri = config.MONGO_URI
my_client = pymongo.MongoClient(mongo_uri)
db_name = "TestMETA"
db = my_client[db_name]
connect(mongo_uri + db_name)  # Connect to MongoDB


def set_up_classification_job(biocontainer: namedtuple, biocontainer_name: str):
    # Set-up database Documents
    user_id = user.insert("Joe Schmo", "Joe.Schmo@hotmail.com", [])
    user_job_id = user_job.insert(user_id=user_id, title="my job title", read_types=["Z"],
                                       classifiers=["A", "B"], mode=JobMode.REAL_READS)
    classification_job_id = classification_job.insert(user_job_id=user_job_id,
                                                           classifier=biocontainer_name,
                                                           fastq_path="test.fastq")

    # Set-up directories
    os.makedirs(os.path.join(config.TEST_DATA_DIR, "jobs", str(user_job_id), biocontainer_name))

    # Copy fastq to job directory
    fastq_path = os.path.join(config.TEST_DATA_DIR, "jobs", str(user_job_id), "test.fastq")
    shutil.copyfile(os.path.join(config.TEST_DATA_DIR, "test.fastq"), fastq_path)

    # Set-up Docker commands
    job_path = os.path.join(config.CONTAINER_DATA_BIND, str(user_job_id))
    result_file = os.path.join(job_path, biocontainer_name, "{}.result".format(biocontainer_name))
    report_file = os.path.join(job_path, biocontainer_name, "{}.report".format(biocontainer_name))
    input_file = os.path.join(job_path, "test.fastq")
    commands = [c.replace("{{VAR_CONTAINER_DB}}", config.CONTAINER_DB_BIND)
                    .replace("{{VAR_RESULT_FILEPATH}}", result_file)
                    .replace("{{VAR_REPORT_FILEPATH}}", report_file)
                    .replace("{{VAR_SEQUENCE_FILEPATH}}", input_file) for c in biocontainer.classify]

    # Set-up volume binds
    db_mount_path = os.path.join(config.TEST_DATA_DIR, "databases", biocontainer.database_name)
    jobs_dir = os.path.join(config.TEST_DATA_DIR, "jobs")
    volumes = {
        db_mount_path: {"bind": config.CONTAINER_DB_BIND},
        jobs_dir: {"bind": config.CONTAINER_DATA_BIND, "mode": "rw"}
    }
    return commands, volumes, classification_job_id, user_job_id


class TestClassify(unittest.TestCase):
    def test_classify_failed(self):
        # TODO
        pass


class TestClassifyMash(unittest.TestCase):
    def setUp(self) -> None:
        # Parse biocontainer.yaml
        self.biocontainer_yaml = open(config.BIOCONTAINERS_PATH, "r")
        _, biocontainers = get_biocontainers_parser(self.biocontainer_yaml)

        self.biocontainer_name = "mash"
        self.biocontainer = pydash.get(biocontainers, self.biocontainer_name)
        self.commands, self.volumes, self.classification_job_id, self.user_job_id = set_up_classification_job(
            biocontainer=self.biocontainer, biocontainer_name=self.biocontainer_name)
        pass

    def test_classify_mash(self):
        succ = classify(commands=self.commands, volumes=self.volumes, biocontainer=self.biocontainer,
                        job_id=ObjectId(self.classification_job_id))

        job_data = classification_job.find_by_id(class_job_id=ObjectId(self.classification_job_id))
        container_id = pydash.get(job_data, "container_id")

        running_containers = docker_client.containers.list()
        running_container_ids = [container.id for container in running_containers]
        self.assertNotIn(container_id, running_container_ids)

        self.assertIsNotNone(pydash.get(job_data, "cpu_time"))
        self.assertIsNotNone(pydash.get(job_data, "wall_clock_time"))
        self.assertIsNotNone(container_id)
        self.assertEqual(pydash.get(job_data, "status"), str(JobStatus.COMPLETED))
        self.assertEqual(succ, True)

        report_file = os.path.join(config.TEST_DATA_DIR, "jobs", str(self.user_job_id),
                                   self.biocontainer_name, "{}.report".format(self.biocontainer_name))
        self.assertTrue(os.path.exists(report_file))
        pass

    def tearDown(self) -> None:
        shutil.rmtree(os.path.join(config.TEST_DATA_DIR, "jobs", str(self.user_job_id)))
        pass


class TestClassifyKraken2(unittest.TestCase):
    def setUp(self) -> None:
        # Parse biocontainer.yaml
        self.biocontainer_yaml = open(config.BIOCONTAINERS_PATH, "r")
        _, biocontainers = get_biocontainers_parser(self.biocontainer_yaml)

        self.biocontainer_name = "kraken2"
        self.biocontainer = pydash.get(biocontainers, self.biocontainer_name)
        self.commands, self.volumes, self.classification_job_id, self.user_job_id = set_up_classification_job(
            biocontainer=self.biocontainer, biocontainer_name=self.biocontainer_name)
        pass

    def test_classify_kraken2(self):
        succ = classify(commands=self.commands, volumes=self.volumes, biocontainer=self.biocontainer,
                        job_id=ObjectId(self.classification_job_id))

        job_data = classification_job.find_by_id(class_job_id=ObjectId(self.classification_job_id))
        container_id = pydash.get(job_data, "container_id")

        running_containers = docker_client.containers.list()
        running_container_ids = [container.id for container in running_containers]
        self.assertNotIn(container_id, running_container_ids)

        self.assertIsNotNone(pydash.get(job_data, "cpu_time"))
        self.assertIsNotNone(pydash.get(job_data, "wall_clock_time"))
        self.assertIsNotNone(container_id)

        self.assertEqual(pydash.get(job_data, "status"), str(JobStatus.COMPLETED))
        self.assertEqual(succ, True)

        report_file = os.path.join(config.TEST_DATA_DIR, "jobs", str(self.user_job_id),
                                   self.biocontainer_name, "{}.report".format(self.biocontainer_name))
        self.assertTrue(os.path.exists(report_file))

        result_file = os.path.join(config.TEST_DATA_DIR, "jobs", str(self.user_job_id),
                                   self.biocontainer_name, "{}.result".format(self.biocontainer_name))
        self.assertTrue(os.path.exists(result_file))
        pass

    def tearDown(self) -> None:
        shutil.rmtree(os.path.join(config.TEST_DATA_DIR, "jobs", str(self.user_job_id)))
        pass
