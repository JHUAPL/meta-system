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

from bson import ObjectId
from pymodm import connect

from shared.config import config
from system.controllers import controllers
from system.models.job_manager import JobStatus
from system.models.schemas_loader import SchemaLoader

connect(config.MONGO_URI)


def insert(user_job_id: ObjectId, read_type: str or None = None) -> ObjectId:
    """
    Insert a new EvaluationJob into the collection.
    :param user_job_id: Which UserJob is associated with this EvaluationJob
    :param read_type: What the read type is for this job
    :return: The ObjectId of the EvaluationJob added
    """
    queue_position = -1

    if read_type is None:
        to_insert = dict(user_job_id=user_job_id, queue_position=queue_position,
                         status=JobStatus.QUEUED)
    else:
        to_insert = dict(user_job_id=user_job_id, read_type=read_type, queue_position=queue_position,
                         status=JobStatus.QUEUED)

    return controllers.insert_one(collection=SchemaLoader.EVALUATION_JOB, data=to_insert)


def find_by_id(eval_job_id: ObjectId, as_json: bool = False) -> str or dict:
    """
    Find Evaluation job using ObjectId
    :param eval_job_id: The Evaluation job id to search for
    :param as_json: Whether or not to return the results as a json
    :return: a str or dict of the Evaluation Job object
    """
    return controllers.find_by_id(collection=SchemaLoader.EVALUATION_JOB, obj_id=eval_job_id, as_json=as_json)


def update_cpu_time(obj_id: ObjectId, time: float):
    """
    How long (in seconds) the specified evaluation took in cpu time.
    :param obj_id: the evaluation job to update
    :param time: how long the evaluation job took in cpu time
    :return: None
    """
    controllers.update_by_id(SchemaLoader.EVALUATION_JOB, obj_id, "cpu_time", time)


def update_wall_clock_time(obj_id: ObjectId, time: float):
    """
    Takes the input time (in seconds) that the evaluation took and updates the wall_clock_time of the document.
    :param time: the datetime duration to update with
    :param obj_id: the document to update
    :return:
    """
    controllers.update_by_id(SchemaLoader.EVALUATION_JOB, obj_id, "wall_clock_time", time)


def update_status(obj_id: ObjectId, new_status: str):
    """
    Update the status of the specified EvaluationJob.
    :param obj_id: the evaluation job to update
    :param new_status: the status to update the evaluation job with
    :return: None
    """
    controllers.update_by_id(SchemaLoader.EVALUATION_JOB, obj_id, "status", new_status)

