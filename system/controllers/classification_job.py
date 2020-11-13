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


def insert(user_job_id: ObjectId, classifier: str, fastq_path: str, read_type: str or None = None) -> ObjectId:
    """
    Insert a new ClassificationJob into the collection.
    :param user_job_id: Which UserJob is associated with this ClassificationJob
    :param classifier: The classifier to use
    :param fastq_path: The input fastq file to read from
    :return: The ObjectId of the ClassificationJob added
    """
    queue_position = -1

    if read_type is None:
        to_insert = dict(user_job_id=user_job_id, classifier=classifier, fastq_path=fastq_path,
                         queue_position=queue_position, status=JobStatus.QUEUED)
        return controllers.insert_one(collection=SchemaLoader.CLASSIFICATION_JOB, data=to_insert)

    else:
        to_insert = dict(user_job_id=user_job_id, classifier=classifier, fastq_path=fastq_path, read_type=read_type,
                         queue_position=queue_position, status=JobStatus.QUEUED)
        return controllers.insert_one(collection=SchemaLoader.CLASSIFICATION_JOB, data=to_insert)


def find_by_id(class_job_id: ObjectId, as_json: bool = False) -> str or dict:
    """
    Find Classification job using ObjectId
    :param class_job_id: The Classification job id to search for
    :param as_json: Whether or not to return the results as a json
    :return: a str or dict of the Classification Job object
    """
    return controllers.find_by_id(collection=SchemaLoader.CLASSIFICATION_JOB, obj_id=class_job_id, as_json=as_json)


def find_specific_job(user_job_id: ObjectId, classifier: str, read_type: str or None = None,
                      as_json: bool = False) -> str or dict:
    """
    Find classification job by user_job_id, read_type, and classifier
    :param user_job_id: The User Job id that triggered this classification job
    :param read_type: The read type you are searching for
    :param classifier: The classifier you are searching for
    :param as_json: Whether or not to return the results as a json
    :return:
    """
    if read_type is not None:
        filter_map = dict(user_job_id=user_job_id, read_type=read_type, classifier=classifier)
    else:
        filter_map = dict(user_job_id=user_job_id, classifier=classifier)
    return controllers.find_by_multi_key_value(collection=SchemaLoader.CLASSIFICATION_JOB, filter_map=filter_map,
                                               as_json=as_json)


def update_wall_clock_time(obj_id: ObjectId, time: float):
    """
    Takes an input float (in seconds) duration and updates the wall_clock_time of the document.
    :param time: the datetime duration to update with
    :param obj_id: the document to update
    :return:
    """
    controllers.update_by_id(SchemaLoader.CLASSIFICATION_JOB, obj_id, "wall_clock_time", time)


def update_max_memory_MBs(obj_id: ObjectId, max_mem: float):
    """
    Update what the max memory of the classification job is.
    :param obj_id: the classification job to update
    :param max_mem: the max memory the classification job takes during the job
    :return: None
    """
    controllers.update_by_id(SchemaLoader.CLASSIFICATION_JOB, obj_id, "max_memory_MBs", max_mem)


def update_cpu_time(obj_id: ObjectId, time: float):
    """
    How long (in seconds) the specified classification took in cpu time.
    :param obj_id: the classification job to update
    :param time: how long the classification job took in cpu time
    :return: None
    """
    controllers.update_by_id(SchemaLoader.CLASSIFICATION_JOB, obj_id, "cpu_time", time)


def update_container_id(obj_id: ObjectId, container_id: str or None):
    """
    Track the id of the container that is currently being run via Docker.
    :param obj_id: the classification job to update
    :param container_id: the container id
    :return: None
    """
    controllers.update_by_id(SchemaLoader.CLASSIFICATION_JOB, obj_id, "container_id", container_id)


def update_status(obj_id: ObjectId, new_status: str):
    """
    Update the status of the specified ClassificationJob.
    :param obj_id: the classification job to update
    :param new_status: the status to update the classification job with
    :return: None
    """
    controllers.update_by_id(SchemaLoader.CLASSIFICATION_JOB, obj_id, "status", new_status)
