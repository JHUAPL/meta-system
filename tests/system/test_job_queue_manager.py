#  **********************************************************************
#  Copyright (C) 2020 Johns Hopkins University Applied Physics Laboratory
#
#  All Rights Reserved.
#  For any other permission, please contact the Legal Office at JHU/APL.
#  **********************************************************************

import os
import unittest

import pydash
from werkzeug.datastructures import ImmutableMultiDict

from shared.config import config
from system.api.jobs import add_child_job, parse_job_payload
from system.controllers import simulation_job, user, user_job
from system.job_queue_manager import push_job, set_job_manager_running_status
from system.models.job_manager import JobManager
from system.models.job_manager import JobType, JobMode


class TestJobManagerPushJob(unittest.TestCase):
    def setUp(self) -> None:
        self.user_id = user.insert(name="Username", email="Usernme@biology.org",
                                   user_jobs=[])
        self.payload_example = ImmutableMultiDict(
            [('title', 'hello'),
             ('filePath', '/test.fastq'),
             ('read_types', "['r9']"),
             ('classifiers', "['centrifuge']")])
        self.title, _, self.read_types, self.classifiers = parse_job_payload(payload=self.payload_example)
        self.filePath = "/mock.tsv"
        self.test_job_manager = JobManager()

        self.user_job_id = user_job.insert(user_id=self.user_id, title=self.title, read_types=self.read_types,
                                           classifiers=self.classifiers, mode=JobMode.SIMULATED_READS)
        self.child_job_id = simulation_job.insert(user_job_id=self.user_job_id, read_type=self.read_types,
                                                  abundance_tsv=os.path.basename(self.filePath),
                                                  number_of_reads=config.DEFAULT_NUM_READS)

        self.job_type = JobType.SIMULATION
        _, _, _, self.job = add_child_job(user_job_id=self.user_job_id, child_job_id=self.child_job_id,
                                          job_type=self.job_type)

    def test_push_job(self):
        push_job(job=self.job, job_queue=self.test_job_manager.queue)
        pushed_job = self.test_job_manager.queue.queue[-1]
        pushed_job_id = pydash.get(pydash.get(pushed_job, "data"), "_id")
        truth = pydash.get(pydash.get(self.job, "data"), "_id")
        self.assertEqual(pushed_job_id, truth)
        return


class TestJobManagerRunningStatus(unittest.TestCase):
    def setUp(self) -> None:
        self.test_job_manager = JobManager()

    def test_running_status(self):
        manager = self.test_job_manager
        set_job_manager_running_status(is_running=True, manager=manager)
        self.assertEqual(self.test_job_manager.running, True)

        set_job_manager_running_status(is_running=False, manager=manager)
        self.assertEqual(self.test_job_manager.running, False)

        set_job_manager_running_status(is_running="True", manager=manager)
        self.assertEqual(self.test_job_manager.running, False)
        return


if __name__ == '_main_':
    unittest.main()
