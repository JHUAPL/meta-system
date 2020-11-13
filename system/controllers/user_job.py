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
from datetime import datetime

import pydash
from bson import ObjectId
from pymodm import connect

from shared.config import config
from shared.log import logger
from system.controllers import controllers, classification_job, simulation_job, evaluation_job
from system.extensions import DockerClient
from system.models.job_manager import JobStatus, JobType, JobMode
from system.models.schemas_loader import SchemaLoader

connect(config.MONGO_URI)

docker_client = DockerClient().get_client()


def insert(user_id: ObjectId, title: str, read_types: list or None, classifiers: list, mode: JobMode) -> ObjectId:
    """
    Insert a new UserJob into the collection.
    :param user_id: Which User is associated with this UserJob
    :param title: user provided string to title their job
    :param read_types: Which read_types this UserJob wants
    :param classifiers: List of classifiers to use
    :param mode: whether this is a real or simulated job.
    :return: The ObjectId of the UserJob added
    """
    if read_types is None:
        to_insert = dict(user_id=user_id, title=title,
                         classifiers=classifiers, mode=mode.value, child_jobs_completed=0,
                         total_child_jobs=0, queue=[], status=JobStatus.QUEUED, hide=False)
        return controllers.insert_one(collection=SchemaLoader.USER_JOB, data=to_insert)

    else:
        to_insert = dict(user_id=user_id, title=title, read_types=read_types,
                         classifiers=classifiers, mode=mode.value, child_jobs_completed=0,
                         total_child_jobs=0, queue=[], status=JobStatus.QUEUED, hide=False)
        return controllers.insert_one(collection=SchemaLoader.USER_JOB, data=to_insert)


def find_all(as_json: bool = False) -> str or dict:
    """
    Returns all documents in the user job collection, as JSON if applicable.
    :param as_json: Flag to signify if collection should be returned in JSON format
    :return: All documents in user job collection
    """
    return controllers.find_all(collection=SchemaLoader.USER_JOB, as_json=as_json)


def find_unhidden_jobs(as_json: bool = False) -> str or dict:
    """
    Returns unhidden documents in the user job collection, as JSON if applicable.
    :param as_json: Flag to signify if collection should be returned in JSON format
    :return: Unhidden documents in user job collection
    """
    return controllers.find_by_key_value(collection=SchemaLoader.USER_JOB, key="hide", value=False, as_json=as_json)


def find_hidden_jobs(as_json: bool = False) -> str or dict:
    """
    Returns the hidden documents in the user job collection, as JSON if applicable.
    :param as_json: Flag to signify if collection should be returned in JSON format
    :return Unhidden documents in user job collection
    """
    return controllers.find_by_key_value(collection=SchemaLoader.USER_JOB, key="hide", value=True, as_json=as_json)


def find_by_id(user_job_id: ObjectId, as_json: bool = False) -> str or dict:
    """
    Find user job using ObjectId
    :param user_job_id: The user job id to search for
    :param as_json: Whether or not to return the results as a json
    :return: a str or dict of User Job object
    """
    return controllers.find_by_id(collection=SchemaLoader.USER_JOB, obj_id=user_job_id, as_json=as_json)


def add_child(obj_id: ObjectId, child_id: ObjectId, job_type: JobType):
    """
    Add child job to this UserJob, updated total jobs and queue.
    :param obj_id: The objectId of the UserJob to update
    :param child_id: The objectId of the child job to be added
    :return: None
    """
    # first get current amount of children jobs
    user_job = find_by_id(user_job_id=obj_id).as_dict()
    previous_num_child = user_job["total_child_jobs"]
    num_child = user_job["total_child_jobs"] + 1
    controllers.update_by_id(collection=SchemaLoader.USER_JOB, obj_id=obj_id, key="total_child_jobs", value=num_child)

    # also update queue to include the new child job
    jobs_queue = user_job["queue"]
    jobs_queue.append((child_id, str(job_type)))
    update_queue(obj_id=obj_id, queue_val=jobs_queue)
    return previous_num_child, num_child


def remove_child(obj_id: ObjectId, child_id: ObjectId, job_type: JobType):
    """
    Remove the completed child job from the queue.
    :param obj_id: The objectId of the UserJob to update
    :param child_id: The objectId of the child job to remove
    :return: None
    """
    # update child jobs completed attribute
    user_job = find_by_id(user_job_id=obj_id).as_dict()
    num_complete = user_job["child_jobs_completed"] + 1
    controllers.update_by_id(collection=SchemaLoader.USER_JOB, obj_id=obj_id, key="child_jobs_completed",
                             value=num_complete)

    # update queue to remove the old child job
    jobs_queue = user_job["queue"]
    try:
        for x in range(len(jobs_queue)):  # remove recently completed job from queue
            [curr_id, curr_type] = jobs_queue[0]
            if curr_id == child_id:
                if curr_type == str(job_type):
                    jobs_queue.pop(x)
    except Exception as e:
        logger.warning("Job queue does not include recently completed job.")

    update_queue(obj_id=obj_id, queue_val=jobs_queue)

    # if there are no more jobs left in queue, and the job wasn't cancelled, update status to be completed
    isCancelled = user_job["status"]
    if isCancelled != "JobStatus.CANCELLED" and len(jobs_queue) == 0:
        update_status(obj_id=obj_id, new_status=str(JobStatus.COMPLETED))


def update_status(obj_id: ObjectId, new_status: str):
    """
    Update the status of an existing UserJob in the collection.
    :param obj_id: The objectId of the UserJob to update
    :param new_status: The new status to give the UserJob
    :return: None
    """
    controllers.update_by_id(collection=SchemaLoader.USER_JOB, obj_id=obj_id, key="status", value=new_status)


def update_queue(obj_id: ObjectId, queue_val: list):
    """
    Update the status of an existing UserJob in the collection.
    :param obj_id: The objectId of the UserJob to update
    :param queue_val: The new status to give the UserJob
    :return: None
    """
    controllers.update_by_id(collection=SchemaLoader.USER_JOB, obj_id=obj_id, key="queue", value=queue_val)


def update_abundance_tsv(obj_id: ObjectId, abundance_tsv: str):
    """
    Update the filename of the abundance TSV of an existing UserJob in the collection.
    :param obj_id: The objectId of the UserJob to update
    :param abundance_tsv: The abundance TSV base filename
    :return: None
    """
    controllers.update_by_id(collection=SchemaLoader.USER_JOB, obj_id=obj_id, key="abundance_tsv", value=abundance_tsv)


def update_completion_time(obj_id: ObjectId, time: datetime):
    """
    Takes the input datetime that the evaluation was completed and updates the completed_datetime of the document.
    :param time: the datetime completion to update with
    :param obj_id: the document to update
    :return:
    """
    controllers.update_by_id(SchemaLoader.USER_JOB, obj_id, "completed_datetime", time)

def update_started_time(obj_id: ObjectId, time: datetime):
    """
    Takes the input datetime that the simulation or classification was started and updated the started_datetime of the document.
    :param time: the datetime started to update with
    :param obj_id: the document to update
    :return:
    """
    controllers.update_by_id(SchemaLoader.USER_JOB, obj_id, "started_datetime", time)



def update_fastq(obj_id: ObjectId, fastq: str):
    """
    Update the filename of the fastq file of an existing UserJob in the collection.
    :param obj_id: The objectId of the UserJob to update
    :param abundance_tsv: The abundance TSV base filename
    :return: None
    """
    controllers.update_by_id(collection=SchemaLoader.USER_JOB, obj_id=obj_id, key="fastq", value=fastq)


def hide_job(obj_id: ObjectId) -> bool:
    """
    Hide a completed job in the UserJob in the collection.
    :param obj_id: The objectId of the UserJob to update
    :return: A boolean to hide the given job
    """
    return controllers.update_by_id(collection=SchemaLoader.USER_JOB, obj_id=obj_id, key="hide", value=True)


def unhide_job(obj_id: ObjectId) -> bool:
    """
    Hide a completed job in the UserJob in the collection.
    :param obj_id: The objectId of the UserJob to update
    :return: A boolean to hide the given job
    """
    return controllers.update_by_id(collection=SchemaLoader.USER_JOB, obj_id=obj_id, key="hide", value=False)


def cancel_job(obj_id: ObjectId) -> (bool, str or None):
    """
    Cancel the existing UserJob in the collection.
    :param obj_id: The objectId of the UserJob to cancel
    :return: True if the cancelled job was currently being run
    """
    user_job = find_by_id(user_job_id=obj_id).as_dict()  # get the user job to cancel
    job_in_progress = False
    jobs_queue = pydash.get(user_job, "queue")
    curr_child_running, curr_job_type_running = jobs_queue[0]

    # set the status to cancelled for all of the jobs that remain in the queue
    for (child_id, child_type) in jobs_queue:
        if child_type == str(JobType.CLASSIFICATION):
            classification_job.update_status(obj_id=child_id, new_status=str(JobStatus.CANCELLED))
        elif child_type == str(JobType.SIMULATION):
            simulation_job.update_status(obj_id=child_id, new_status=str(JobStatus.CANCELLED))
        elif child_type == str(JobType.EVALUATION):
            evaluation_job.update_status(obj_id=child_id, new_status=str(JobStatus.CANCELLED))

    container_id = None
    user_job_status = pydash.get(user_job, "status")  # get current status to see if this is running or just queued
    if user_job_status == "JobStatus.PROCESSING":  # if the job is already running
        job_in_progress = True
        # stop the Docker container for this job only for SIMULATION or CLASSIFICATION
        if curr_job_type_running == str(JobType.SIMULATION) or curr_job_type_running == str(JobType.CLASSIFICATION):
            if curr_job_type_running == str(JobType.SIMULATION):
                job_data = simulation_job.find_by_id(sim_job_id=curr_child_running).as_dict()
                container_id = pydash.get(job_data, "container_id", None)
                simulation_job.update_container_id(obj_id=curr_child_running, container_id=None)

            elif curr_job_type_running == str(JobType.CLASSIFICATION):
                job_data = classification_job.find_by_id(class_job_id=curr_child_running).as_dict()
                container_id = pydash.get(job_data, "container_id", None)
                classification_job.update_container_id(obj_id=curr_child_running, container_id=None)

    # update status and return success
    update_status(obj_id=obj_id, new_status=str(JobStatus.CANCELLED))

    return job_in_progress, container_id


def delete_job(obj_id: ObjectId) -> bool:
    """
    Delete the existing UserJob in the collection.
    :param obj_id: The objectId of the UserJob to delete
    :return: True if job was successfully deleted
    """
    user_job = find_by_id(user_job_id=obj_id).as_dict()  # get the user_job_id to delete
    try:
        if user_job["_id"] is not None:
            controllers.delete_by_id(collection=SchemaLoader.USER_JOB, obj_id=user_job["_id"]) #delete doc from mongoDB
            return user_job
    except Exception as e:
        logger.error(repr(e))
