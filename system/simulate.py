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
import time
from datetime import datetime

import pydash
from bson import ObjectId

from shared.config import config
from shared.log import logger
from system import DockerClient
from system.controllers import simulation_job, user_job
from system.models.job_manager import JobStatus, JobType
from system.utils.job_failure import handle_fail
from system.utils.readtypes import get_read_types

docker_client = DockerClient().get_client()


def run_simulation_job(job: dict):
    """
    Simulate read type specified in job using meta_simulator Docker container. Example command constructed:
    ```
    docker run -it -v $PWD/data:/data meta_simulator_test:latest /bin/bash -c "./scripts/sim_module_wrapper.sh -t 2 -i
    /data/strawman_envassay.tsv -p r9 -r 100 -o /data/test/"
    ```
    """
    # Update simulation job status
    user_job_id = pydash.get(job, "user_job_id")
    sim_job_id = pydash.get(job, "_id")
    t_start = datetime.now()
    user = user_job.find_by_id(user_job_id=user_job_id).as_dict()
    completed_jobs = user["child_jobs_completed"]
    if completed_jobs == 0:
        user_job.update_started_time(obj_id=user_job_id, time=t_start)
    if sim_job_id is None:
        handle_fail(job_type=JobType.SIMULATION, job_id=sim_job_id, message="JOB ID NOT INCLUDED!")
        return
    simulation_job.update_status(obj_id=sim_job_id, new_status=str(JobStatus.PROCESSING))
    user_job.update_status(obj_id=user_job_id, new_status=str(JobStatus.PROCESSING))
    logger.info("RUNNING SIMULATION FOR USER JOB {}".format(str(user_job_id)))

    # Determine read type to simulate
    read_type = pydash.get(job, "read_type", None)
    read_type_names, _ = get_read_types()
    if read_type is None or read_type not in read_type_names:
        handle_fail(job_type=JobType.SIMULATION, job_id=sim_job_id, message="INVALID READ TYPE {}!".format(read_type))
    logger.info("SIMULATING READ TYPE {}".format(read_type))

    # Make directory where simulated fastq file will be written to
    # /data/jobs/<user_job_id>/<read_type>/
    save_dir_local = os.path.join(config.JOBS_DIR, str(user_job_id), read_type)
    if not os.path.exists(save_dir_local):
        os.mkdir(save_dir_local)
    save_dir_container = save_dir_local.replace(config.JOBS_DIR, config.CONTAINER_DATA_BIND)

    # Abundance tsv expected to be located at /data/jobs/<user_job_id>/<read_type>/*.tsv
    tsv_filename = pydash.get(job, "abundance_tsv", None)
    if tsv_filename is None:
        handle_fail(job_type=JobType.SIMULATION, job_id=sim_job_id, message="NO TSV FILENAME PROVIDED!")

    # Construct path to TSV on local machine
    abundance_tsv_local = os.path.join(config.JOBS_DIR, str(user_job_id), tsv_filename)

    # Construct path to TSV within Docker container
    abundance_tsv_container = abundance_tsv_local.replace(config.JOBS_DIR, config.CONTAINER_DATA_BIND)

    volumes = {config.JOBS_DIR: {"bind": config.CONTAINER_DATA_BIND, "mode": "rw"}}
    wall_clock_time, cpu_time = simulate(sim_job_id=sim_job_id, abundance_tsv_in_container=abundance_tsv_container,
                                         read_type=read_type, output_dir_in_container=save_dir_container,
                                         volumes=volumes)

    logger.info("SIMULATION {} FINISHED FOR USER JOB {} IN {} ({} CPU TIME)".format(read_type,
                                                                                    str(user_job_id),
                                                                                    str(wall_clock_time),
                                                                                    str(cpu_time)))
    return


def simulate(sim_job_id: ObjectId, abundance_tsv_in_container: str, read_type: str, output_dir_in_container: str,
             volumes: dict):
    # Construct command to run in META simulator
    sim_command = "./scripts/sim_module_wrapper.sh -t {} -i {} -p {} -o {}".format(config.NUM_SIM_THREADS,
                                                                                   abundance_tsv_in_container,
                                                                                   read_type,
                                                                                   output_dir_in_container)
    full_command = ["/bin/bash", "-c", sim_command]

    t_start = datetime.now()
    try:
        # Run Docker
        job_container = docker_client.containers.create(image=config.META_SIMULATOR_IMAGE_NAME,
                                                        volumes=volumes,
                                                        command=full_command,
                                                        detach=True)
        t_start_cpu = datetime.fromtimestamp(time.process_time())
        simulation_job.update_container_id(obj_id=sim_job_id, container_id=job_container.id)
        job_container.start()
        logger.debug("RUNNING CONTAINER {}".format(job_container.id))
    except Exception as e:
        handle_fail(job_type=JobType.SIMULATION, job_id=sim_job_id, message="PROBLEM RUNNING DOCKER", more_info=e)

        # Clean up after exception
        job_container.stop(timeout=10)
        job_container.remove(v=True, force=True)
        return False

    # Print logs for classification
    for log in job_container.logs(follow=True, stream=True):
        print(log.decode("utf-8"))

    # Compute timing metrics
    t_end_cpu = datetime.fromtimestamp(time.process_time())
    t_dur_cpu = t_end_cpu - t_start_cpu

    t_end = datetime.now()
    t_dur = t_end - t_start

    # Update performance metrics for job
    simulation_job.update_cpu_time(obj_id=sim_job_id, time=t_dur_cpu.total_seconds())
    simulation_job.update_wall_clock_time(obj_id=sim_job_id, time=t_dur.total_seconds())
    simulation_job.update_status(obj_id=sim_job_id, new_status=str(JobStatus.COMPLETED))

    # Clean up after job executes
    job_container.stop(timeout=10)
    job_container.remove(v=True, force=True)

    # clean_up_files(directory=save_dir_local, keep=[config.SIMULATED_FASTQ_NAME, "error.log"])
    return t_dur, t_dur_cpu


def clean_up_files(directory: str, keep: list):
    # FIXME: This doesn't work
    contents = os.listdir(directory)
    for d in contents:
        path = os.path.join(directory, d)
        if any([k in d for k in keep]):
            continue
        elif os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=True)
        elif os.path.isfile(path):
            os.remove(path)
    return
