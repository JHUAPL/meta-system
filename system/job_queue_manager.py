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

import queue
import time

import psutil
import pydash
from pebble import concurrent

from shared.log import logger
from system.classify import run_classification_job
from system.controllers import user_job, classification_job, controllers
from system.evaluate import run_evaluation_job
from system.metrics.classification.computational_resources import calculate_max_memory_megabytes

from system.models.job_manager import JobType, JobManager, JobStatus
from system.models.schemas_loader import SchemaLoader
from system.simulate import run_simulation_job

job_manager = JobManager()
@concurrent.thread
def job_queue_watchdog():
    """
    Check queue every second for new job and invoke proper function. Checks if job status is cancelled prior to run
    """
    # Pop job from queue when previous job is finished
    logger.debug("STARTING JOB QUEUE WATCHDOG")
    jobs_finished = True
    job_mode = False
    while True:
        time.sleep(1)  # check every second
        if not job_manager.running:  # if the job mgr is not running (i.e. available to run a new job)
            if not job_manager.queue.empty():  # and there is a job in the queue to run
                job = job_manager.queue.get()
                if job is not None:
                    jobs_finished = True
                    job_manager.running = True  # job mgr is busy now
                    curr_coll = None
                    job_type = pydash.get(job, "type")
                    data = pydash.get(job, "data") 

                    if job_type == JobType.SIMULATION:
                        curr_coll = SchemaLoader.SIMULATION_JOB
                    elif job_type == JobType.CLASSIFICATION:
                        curr_coll = SchemaLoader.CLASSIFICATION_JOB
                    elif job_type == JobType.EVALUATION:
                        curr_coll = SchemaLoader.EVALUATION_JOB

                    # first get actual job reference, not one in job queue to see if cancelled
                    job_id = data._id
                    job_dict = controllers.find_by_id(collection=curr_coll, obj_id=job_id).as_dict()
                    job_status = job_dict["status"]

                    if job_status == str(JobStatus.CANCELLED):  # double check job is not cancelled
                        logger.error("Job {} has been cancelled and should not run.".format(str(job_id)))
                    else:
                        if job_type == JobType.SIMULATION:  # run simulation job
                            run_simulation_job(job=data)
                            job_mode = True
                        elif job_type == JobType.CLASSIFICATION:  # run classification job
                            get_job_memory_usage(job=data)
                            run_classification_job(job=data, job_mode=job_mode)
                        elif job_type == JobType.EVALUATION:  # run evaluation job
                            run_evaluation_job(job=data)

                        # update UserJob to reflect child job completion
                        job_dict = controllers.find_by_id(collection=curr_coll, obj_id=job_id).as_dict()
                        job_status = job_dict["status"]
                        if job_status != str(JobStatus.COMPLETED):
                            logger.error("Job {} finished with error.".format(str(job_id)))
                        data = data.as_dict()
                        user_job.remove_child(obj_id=data["user_job_id"], child_id=job_id, job_type=job_type)

                    job_manager.running = False  # job manager should be ready to work on another job
            elif jobs_finished:
                jobs_finished = False
                logger.info("WAITING FOR NEW JOBS...")


@concurrent.thread
def push_job(job: dict, job_queue: queue.Queue = job_manager.queue):
    # Push to job queue (block until free spot is available)
    job_queue.put(job, block=True)
    data = pydash.get(job, "data")
    logger.info("PUT JOB {} IN QUEUE".format(pydash.get(data, "_id")))
    return pydash.get(data, "_id")


@concurrent.thread
def get_job_memory_usage(job: dict):  # assumes jobs run in sequence
    logger.debug("STARTING MEMORY SENSOR FOR JOB {}".format(pydash.get(job, "user_job_id")))

    max_mem_used = 0
    while job_manager.running:
        max_mem_used = calculate_max_memory_megabytes(curr_mem_used=max_mem_used, sys_mem=psutil.virtual_memory())
        time.sleep(1)  # check every second

    logger.info("MEMORY USAGE FOR JOB {} IS {:.0f} MB".format(pydash.get(job, "user_job_id"), max_mem_used))
    classification_job.update_max_memory_MBs(obj_id=pydash.get(job, "_id"), max_mem=max_mem_used)


@concurrent.thread
def set_job_manager_running_status(is_running: bool, manager: JobManager = job_manager):
    # check is_running type
    if type(is_running) != bool:
        logger.warning("JOB MANAGER RUNNING STATUS MUST BE BOOLEAN")
        return
    manager.running = is_running


@concurrent.thread
def restart_job_queue_watchdog():  # restart job queue watchdog after thread is killed
    logger.info("RESTARTING QUEUE WATCHDOG...")
    job_queue_watchdog()  # restart job queue watchdog after thread is killed
