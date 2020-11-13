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

from shared.log import logger
from system.controllers import simulation_job, classification_job, evaluation_job
from system.models.job_manager import JobType, JobStatus


def handle_fail(job_type: JobType or None = None, job_id: ObjectId or None = None, message: str = "", more_info=None):
    logger.error(message, exc_info=more_info)  # log the error

    if job_type is not None and job_id is not None:
        # update the job collections to reflect failed job
        job_ref = dict()
        fail_str = str(JobStatus.FAILED)

        if job_type == JobType.SIMULATION:
            simulation_job.update_status(obj_id=job_id, new_status=fail_str)
            job_ref = simulation_job.find_by_id(sim_job_id=job_id)

        elif job_type == JobType.CLASSIFICATION:
            classification_job.update_status(obj_id=job_id, new_status=fail_str)
            job_ref = classification_job.find_by_id(class_job_id=job_id)

        elif job_type == JobType.EVALUATION:
            evaluation_job.update_status(obj_id=job_id, new_status=fail_str)
            job_ref = evaluation_job.find_by_id(eval_job_id=job_id)

        user_job_id = job_ref.as_dict()["user_job_id"]
        # we might want to deal with this differently than having the entire user job fail
        # user_job.update_status(obj_id=user_job_id, new_status=fail_status)
