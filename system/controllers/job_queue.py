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

from pymodm import connect

from shared.config import config
from system.controllers.controllers import *
from system.models.job_manager import JobStatus
from system.models.schemas_loader import SchemaLoader

connect(config.MONGO_URI)


def insert(job_type: Enum, job_id: ObjectId) -> ObjectId:
    """
    Insert a new Job into the JobQueue collection.
    :param job_type: choices=["Classification", "Evaluation", "Simulation"]
    :param job_id: the ID of the job to add to the queue
    :return: The ObjectId of the JobQueue Job added
    """
    queue_position = -1

    to_insert = dict(job_type=job_type, job_id=job_id, queue_position=queue_position, status=JobStatus.QUEUED)
    return insert_one(collection=SchemaLoader.JOB_QUEUE, data=to_insert)


def delete(obj_id: ObjectId):
    """
    Delete Job specified by data in JobQueue collection.
    Job should be complete.
    :param obj_id: the document ID to delete
    :return: None
    """
    delete_by_id(SchemaLoader.JOB_QUEUE, obj_id)
