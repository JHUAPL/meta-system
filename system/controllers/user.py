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


def insert(name: str, email: str, user_jobs: list) -> ObjectId:
    """
    Insert a new User into the collection.
    :param name: Name of the user to create
    :param email: Email of the user
    :param user_jobs: List of UserJobs associated with this User
    :return: The ObjectId of the UserJob added
    """
    queue_position = -1

    to_insert = dict(name=name, email=email, user_jobs=user_jobs, queue_position=queue_position,
                     status=JobStatus.QUEUED)

    return insert_one(collection=SchemaLoader.USER, data=to_insert)


def find_all_user_jobs(user_id: ObjectId, as_json: bool = False) -> str or dict:
    """
    Find by user all documents in their UserJob collection.
    :param as_json: whether or not to return the results as a json
    :param obj_id: The object id to find all the jobs for
    :return: a str or dict of all the UserJobs
    """
    user_jobs = find_all(SchemaLoader.USER_JOB, as_json)
    user_jobs_obj = []
    for job in user_jobs:
        if job.user_id == user_id:
            user_jobs_obj.append(job)

    return list(map(lambda d: d.as_json() if as_json else d, user_jobs_obj))  # return each as a json if desired
