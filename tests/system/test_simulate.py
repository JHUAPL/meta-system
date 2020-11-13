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
import glob
import os
import shutil
import unittest

import pydash
import pymongo
from pymodm import connect

from shared.config import config
from shared.log import logger
from system.controllers import user, user_job, simulation_job
from system.extensions import DockerClient
from system.models.job_manager import JobMode, JobStatus
from system.simulate import simulate

docker_client = DockerClient().get_client()

# Set-up mongo database connection
mongo_uri = config.MONGO_URI
my_client = pymongo.MongoClient(mongo_uri)
db_name = "TestMETA"
db = my_client[db_name]
connect(mongo_uri + db_name)  # Connect to MongoDB


class TestSimulation(unittest.TestCase):
    def setUp(self) -> None:
        # Set-up database Documents
        user_id = user.insert("Joe Schmo", "Joe.Schmo@hotmail.com", [])
        self.user_job_id = user_job.insert(user_id=user_id, title="my job title", read_types=["Z"],
                                           classifiers=["A", "B"], mode=JobMode.REAL_READS)
        self.tsv_name = "mock.tsv"

        src = os.path.join(config.TEST_DATA_DIR, self.tsv_name)
        dst = os.path.join(config.TEST_DATA_DIR, "jobs", str(self.user_job_id), self.tsv_name)
        os.mkdir(os.path.join(config.TEST_DATA_DIR, "jobs", str(self.user_job_id)))
        shutil.copyfile(src=src, dst=dst)

        self.abundance_tsv_in_container = os.path.join(config.CONTAINER_DATA_BIND, str(self.user_job_id), self.tsv_name)

        self.job_path = os.path.join(config.TEST_DATA_DIR, "jobs")
        self.volumes = {self.job_path: {"bind": config.CONTAINER_DATA_BIND, "mode": "rw"}}
        pass

    def test_simulate_miseq(self):
        read_type = "miseq"
        output_dir_in_container = os.path.join(config.CONTAINER_DATA_BIND, str(self.user_job_id), read_type)
        os.mkdir(os.path.join(self.job_path, str(self.user_job_id), read_type))

        sim_job_id = simulation_job.insert(user_job_id=self.user_job_id, read_type=read_type,
                                           abundance_tsv=self.tsv_name, number_of_reads=config.DEFAULT_NUM_READS)

        _, _ = simulate(sim_job_id=sim_job_id, abundance_tsv_in_container=self.abundance_tsv_in_container,
                        read_type=read_type, output_dir_in_container=output_dir_in_container,
                        volumes=self.volumes)

        # Check file is written
        true_simulated_fastq_path = os.path.join(config.TEST_DATA_DIR, "jobs", str(self.user_job_id), read_type,
                                                 config.SIMULATED_FASTQ_NAME)
        self.assertTrue(os.path.exists(true_simulated_fastq_path))

        # Check evaluation job attributes are updated
        sim_job_data = simulation_job.find_by_id(sim_job_id=sim_job_id)
        self.assertIsNotNone(pydash.get(sim_job_data, "cpu_time"))
        self.assertIsNotNone(pydash.get(sim_job_data, "wall_clock_time"))
        self.assertEqual(pydash.get(sim_job_data, "status"), str(JobStatus.COMPLETED))

    def test_simulate_iseq(self):
        read_type = "iseq"
        output_dir_in_container = os.path.join(config.CONTAINER_DATA_BIND, str(self.user_job_id), read_type)
        os.mkdir(os.path.join(self.job_path, str(self.user_job_id), read_type))

        sim_job_id = simulation_job.insert(user_job_id=self.user_job_id, read_type=read_type,
                                           abundance_tsv=self.tsv_name, number_of_reads=config.DEFAULT_NUM_READS)

        _, _ = simulate(sim_job_id=sim_job_id, abundance_tsv_in_container=self.abundance_tsv_in_container,
                        read_type=read_type, output_dir_in_container=output_dir_in_container,
                        volumes=self.volumes)

        # Check file is written
        true_simulated_fastq_path = os.path.join(config.TEST_DATA_DIR, "jobs", str(self.user_job_id), read_type,
                                                 config.SIMULATED_FASTQ_NAME)
        self.assertTrue(os.path.exists(true_simulated_fastq_path))

        # Check evaluation job attributes are updated
        sim_job_data = simulation_job.find_by_id(sim_job_id=sim_job_id)
        self.assertIsNotNone(pydash.get(sim_job_data, "cpu_time"))
        self.assertIsNotNone(pydash.get(sim_job_data, "wall_clock_time"))
        self.assertEqual(pydash.get(sim_job_data, "status"), str(JobStatus.COMPLETED))

    def test_simulate_r9(self):
        read_type = "r9"
        output_dir_in_container = os.path.join(config.CONTAINER_DATA_BIND, str(self.user_job_id), read_type)
        os.mkdir(os.path.join(self.job_path, str(self.user_job_id), read_type))

        sim_job_id = simulation_job.insert(user_job_id=self.user_job_id, read_type=read_type,
                                           abundance_tsv=self.tsv_name, number_of_reads=config.DEFAULT_NUM_READS)

        _, _ = simulate(sim_job_id=sim_job_id, abundance_tsv_in_container=self.abundance_tsv_in_container,
                        read_type=read_type, output_dir_in_container=output_dir_in_container,
                        volumes=self.volumes)

        # Check file is written
        true_simulated_fastq_path = os.path.join(config.TEST_DATA_DIR, "jobs", str(self.user_job_id), read_type,
                                                 config.SIMULATED_FASTQ_NAME)
        self.assertTrue(os.path.exists(true_simulated_fastq_path))

        # Check evaluation job attributes are updated
        sim_job_data = simulation_job.find_by_id(sim_job_id=sim_job_id)
        self.assertIsNotNone(pydash.get(sim_job_data, "cpu_time"))
        self.assertIsNotNone(pydash.get(sim_job_data, "wall_clock_time"))
        self.assertEqual(pydash.get(sim_job_data, "status"), str(JobStatus.COMPLETED))

    def test_simulate_flg(self):
        read_type = "flg"
        output_dir_in_container = os.path.join(config.CONTAINER_DATA_BIND, str(self.user_job_id), read_type)
        os.mkdir(os.path.join(self.job_path, str(self.user_job_id), read_type))

        sim_job_id = simulation_job.insert(user_job_id=self.user_job_id, read_type=read_type,
                                           abundance_tsv=self.tsv_name, number_of_reads=config.DEFAULT_NUM_READS)

        _, _ = simulate(sim_job_id=sim_job_id, abundance_tsv_in_container=self.abundance_tsv_in_container,
                        read_type=read_type, output_dir_in_container=output_dir_in_container,
                        volumes=self.volumes)

        # Check file is written
        true_simulated_fastq_path = os.path.join(config.TEST_DATA_DIR, "jobs", str(self.user_job_id), read_type,
                                                 config.SIMULATED_FASTQ_NAME)
        self.assertTrue(os.path.exists(true_simulated_fastq_path))

        # Check evaluation job attributes are updated
        sim_job_data = simulation_job.find_by_id(sim_job_id=sim_job_id)
        self.assertIsNotNone(pydash.get(sim_job_data, "cpu_time"))
        self.assertIsNotNone(pydash.get(sim_job_data, "wall_clock_time"))
        self.assertEqual(pydash.get(sim_job_data, "status"), str(JobStatus.COMPLETED))

    def tearDown(self) -> None:
        path = os.path.join(config.TEST_DATA_DIR, "jobs", str(self.user_job_id))
        files = glob.glob(path + "/**/*", recursive=True)
        dirs = [path]
        for f in files:
            try:
                if os.path.isfile(f):
                    os.unlink(f)
                elif os.path.isdir(f):
                    dirs.append(f)
            except OSError as e:
                logger.error("Cannot delete {}!".format(f))

        # delete directories after files are deleted
        num_attempts = 10
        attempts = 0
        while len(dirs) > 0 and attempts < num_attempts:
            for d in dirs:
                try:
                    os.rmdir(d)
                    dirs.remove(d)  # remove from list
                except OSError as e:
                    attempts += 1
                    continue
