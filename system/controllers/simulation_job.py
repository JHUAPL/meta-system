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


def insert(user_job_id: ObjectId, read_type: str, abundance_tsv: str, number_of_reads: int) -> ObjectId:
    """
    Insert a new SimulationJob into the collection.
    :param user_job_id: Which UserJob is associated with this SimulationJob
    :param read_type: The read_type for this SimulationJob
    :param abundance_tsv: The abundance profile tsv for this SimulationJob
    :param number_of_reads: Number of reads to do for this SimulationJob
    :return: The ObjectId of the SimulationJob added
    """
    queue_position = -1

    to_insert = dict(user_job_id=user_job_id, read_type=read_type, abundance_tsv=abundance_tsv,
                     number_of_reads=number_of_reads, queue_position=queue_position, status=JobStatus.QUEUED)

    return controllers.insert_one(collection=SchemaLoader.SIMULATION_JOB, data=to_insert)


def find_by_id(sim_job_id: ObjectId, as_json: bool = False) -> str or dict:
    """
    Find Simulation job using ObjectId
    :param sim_job_id: The Simulation job id to search for
    :param as_json: Whether or not to return the results as a json
    :return: a str or dict of the Simulation Job object
    """
    return controllers.find_by_id(collection=SchemaLoader.SIMULATION_JOB, obj_id=sim_job_id, as_json=as_json)


def find_specific_job(user_job_id: ObjectId, read_type: str, as_json: bool = False) -> str or dict:
    """
    Find classification job by user_job_id, read_type, and classifier
    :param user_job_id: The User Job id that triggered this classification job
    :param read_type: The read type you are searching for
    :param classifier: The classifier you are searching for
    :param as_json: Whether or not to return the results as a json
    :return:
    """
    filter_map = dict(user_job_id=user_job_id, read_type=read_type)
    return controllers.find_by_multi_key_value(collection=SchemaLoader.SIMULATION_JOB, filter_map=filter_map,
                                               as_json=as_json)


def update_cpu_time(obj_id: ObjectId, time: float):
    """
    How long (in seconds) the specified simulation took in cpu time.
    :param obj_id: the simulation job to update
    :param time: how long the simulation job took in cpu time
    :return: None
    """
    controllers.update_by_id(SchemaLoader.SIMULATION_JOB, obj_id, "cpu_time", time)


def update_wall_clock_time(obj_id: ObjectId, time: float):
    """
    Takes the input time (in seconds) that the simulation took and updates the wall_clock_time of the document.
    :param time: the datetime duration to update with
    :param obj_id: the document to update
    :return:
    """
    controllers.update_by_id(SchemaLoader.SIMULATION_JOB, obj_id, "wall_clock_time", time)


def update_container_id(obj_id: ObjectId, container_id: str or None):
    """
    Track the id of the container that is currently being run via Docker.
    :param obj_id: the simulation job to update
    :param container_id: the container id
    :return: None
    """
    controllers.update_by_id(SchemaLoader.SIMULATION_JOB, obj_id, "container_id", container_id)


def update_status(obj_id: ObjectId, new_status: str):
    """
    Update the status of the specified SimulationJob.
    :param obj_id: the simulation job to update
    :param new_status: the status to update the simulation job with
    :return: None
    """
    controllers.update_by_id(SchemaLoader.SIMULATION_JOB, obj_id, "status", new_status)

