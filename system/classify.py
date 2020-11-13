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
import time
from collections import namedtuple
from datetime import datetime

import pydash
from bson import ObjectId

from shared.config import config
from shared.log import logger
from system.controllers import classification_job, user_job
from system.extensions import DockerClient
from system.models.job_manager import JobStatus, JobType
from system.utils.biocontainers import get_biocontainers, parse_container_command
from system.utils.job_failure import handle_fail

docker_client = DockerClient().get_client()


def run_classification_job(job: dict, job_mode: bool):
    t_job_start = datetime.now()
    user_job_id = pydash.get(job, "user_job_id")
    class_job_id = pydash.get(job, "_id")
    user = user_job.find_by_id(user_job_id=user_job_id).as_dict()
    completed_jobs = user["child_jobs_completed"]
    if (job_mode is False) and (completed_jobs == 0):
        user_job.update_started_time(obj_id=user_job_id, time=t_job_start)
    job_mode = False

    if class_job_id is None:
        handle_fail(job_type=JobType.CLASSIFICATION, job_id=class_job_id, message="JOB ID NOT INCLUDED!")
        return

    # Parse job object
    res = parse_job_data(job=job)
    if res is None:
        return
    user_job_id, class_job_id, classifier, fastq_filepath = res
    classification_job.update_status(obj_id=class_job_id, new_status=str(JobStatus.PROCESSING))
    user_job.update_status(obj_id=user_job_id, new_status=str(JobStatus.PROCESSING))
    logger.info("RUNNING CLASSIFICATION FOR JOB {}".format(str(user_job_id)))

    # Get classifier information
    classifier = pydash.get(job, "classifier", None)
    _, biocontainers_info = get_biocontainers()
    biocontainer = pydash.get(biocontainers_info, classifier)
    logger.debug("USING BIOCONTAINER: {}".format(biocontainer))

    _, ext = os.path.splitext(fastq_filepath)
    file_formats = biocontainer.file_formats
    if ext[1:] not in file_formats:  # index [1:] removes leading . from extension
        handle_fail(job_type=JobType.CLASSIFICATION, job_id=class_job_id,
                    message="BIOCONTAINER DOES NOT ACCEPT {} FILES!".format(ext))
        return

    # Set-up Docker volumes
    db_mount_path = os.path.join(config.BIOCONTAINER_DB_DIR, biocontainer.database_name)
    if not os.path.exists(db_mount_path):
        handle_fail(job_type=JobType.CLASSIFICATION, job_id=class_job_id,
                    message="BIOCONTAINER DATABASE {} DOES NOT EXIST".format(db_mount_path))
        return

    volumes = {
        db_mount_path: {"bind": config.CONTAINER_DB_BIND},
        config.JOBS_DIR: {"bind": config.CONTAINER_DATA_BIND, "mode": "rw"}
    }

    # Make job directories and construct output paths
    result_filepath, report_filepath, input_filepath = setup_job_directories(fastq_filepath=fastq_filepath,
                                                                             classifier=classifier)

    # Parse Docker commands
    classify_commands = []
    if biocontainer.classify:
        for c in biocontainer.classify:
            classify_command = parse_container_command(command=c, result_file=result_filepath,
                                                       report_file=report_filepath, input_file=input_filepath)
            classify_commands.append(classify_command)
    else:
        handle_fail(job_type=JobType.CLASSIFICATION, job_id=class_job_id,
                    message="CLASSIFY COMMAND NOT PROVIDED FOR BIOCONTAINER. NOT RUNNING CLASSIFICATION!")
        return False

    report_commands = []
    if biocontainer.report:
        for c in biocontainer.report:
            report_command = parse_container_command(command=c, result_file=result_filepath,
                                                     report_file=report_filepath, input_file=input_filepath)
            report_commands.append(report_command)

    # Run classifier
    classify_success = False
    if classify_commands:
        logger.debug("BEGIN CLASSIFYING")
        classify_success = classify(commands=classify_commands, volumes=volumes, biocontainer=biocontainer,
                                    job_id=class_job_id)
        if not classify_success:
            handle_fail(job_type=JobType.CLASSIFICATION, job_id=class_job_id, message="CLASSIFICATION FAILED! ABORT.")
            return False

    # Write report
    if report_commands and classify_success:
        logger.debug("WRITING REPORT")
        report_success = report(commands=report_commands, biocontainer=biocontainer, volumes=volumes,
                                report_filepath=report_filepath, class_job_id=class_job_id)
        if not report_success:
            handle_fail(job_type=JobType.CLASSIFICATION, job_id=class_job_id, message="REPORTING FAILED! ABORT.")
            return False

    # Finish Job
    t_job_end = datetime.now()
    t_job_dur = t_job_end - t_job_start

    logger.info(
        "FINISHED {} CLASSIFICATION JOB FOR USER JOB {} IN {} ".format(classifier, str(user_job_id), str(t_job_dur)))
    return


def classify(commands: list, volumes: dict, biocontainer: namedtuple, job_id: ObjectId) -> bool:
    for command in commands:
        logger.debug("CLASSIFY COMMAND: {}".format(command))

        t_classify_start = datetime.now()
        try:
            job_container = docker_client.containers.create(image=biocontainer.image,
                                                            volumes=volumes,
                                                            command=command,
                                                            detach=True)

            t_classify_start_cpu = datetime.fromtimestamp(time.process_time())
            classification_job.update_container_id(obj_id=job_id, container_id=job_container.id)
            job_container.start()
            logger.debug("RUNNING CONTAINER {}".format(job_container.id))

        except Exception as e:
            handle_fail(job_type=JobType.CLASSIFICATION, job_id=job_id, message="PROBLEM RUNNING DOCKER",
                        more_info=e)

            # Clean up after exception
            job_container.stop(timeout=10)
            job_container.remove(v=True, force=True)
            return False

        # Print logs for classification
        for log in job_container.logs(follow=True, stream=True):
            print(log.decode("utf-8"))

        t_classify_end_cpu = datetime.fromtimestamp(time.process_time())
        t_classify_dur_cpu = t_classify_end_cpu - t_classify_start_cpu

        t_classify_end = datetime.now()
        t_classify_dur = t_classify_end - t_classify_start

        # Update performance metrics for job.
        classification_job.update_cpu_time(obj_id=job_id, time=t_classify_dur_cpu.total_seconds())
        classification_job.update_wall_clock_time(obj_id=job_id, time=t_classify_dur.total_seconds())
        classification_job.update_status(obj_id=job_id, new_status=str(JobStatus.COMPLETED))

        # Clean up after job executes
        job_container.stop(timeout=10)
        job_container.remove(v=True, force=True)

    return True


def report(commands: list, biocontainer: namedtuple, volumes: dict, report_filepath: str, class_job_id: ObjectId):
    for command in commands:
        logger.debug("REPORT COMMAND: {}".format(command))

        t_report_start = datetime.now()
        try:
            job_container = docker_client.containers.create(image=biocontainer.image,
                                                            volumes=volumes,
                                                            command=command,
                                                            detach=True)
            classification_job.update_container_id(obj_id=class_job_id, container_id=job_container.id)
            job_container.start()
            logger.debug("RUNNING CONTAINER {}".format(job_container.id))
        except Exception as e:
            handle_fail(job_type=JobType.CLASSIFICATION, job_id=class_job_id, message="PROBLEM RUNNING DOCKER",
                        more_info=e)

            # Clean up after exception
            job_container.stop(timeout=10)
            job_container.remove(v=True, force=True)
            return False

        # Print logs for reporting
        with open(report_filepath.replace(config.CONTAINER_DATA_BIND, config.JOBS_DIR), "w") as f:
            for log in job_container.logs(follow=True, stream=True):
                f.write(log.decode("utf-8"))
                # f.write("\n")

        t_report_end = datetime.now()
        t_report_dur = t_report_end - t_report_start

        # Clean up after job executes
        job_container.stop(timeout=10)
        job_container.remove(v=True, force=True)

        logger.info("REPORTING FINISHED IN {}".format(str(t_report_dur)))
    return True


def parse_job_data(job: dict) -> (ObjectId, ObjectId, str, str) or None:
    user_job_id = pydash.get(job, "user_job_id")
    class_job_id = pydash.get(job, "_id")
    if class_job_id is None:
        handle_fail(job_type=JobType.CLASSIFICATION, job_id=class_job_id, message="JOB ID NOT INCLUDED!")
        return None
    classification_job.update_status(obj_id=class_job_id, new_status=str(JobStatus.PROCESSING))
    logger.info("RUNNING CLASSIFICATION FOR JOB {}".format(str(user_job_id)))

    # Get classifier information
    classifier = pydash.get(job, "classifier", None)

    fastq_filepath = pydash.get(job, "fastq_path", None)
    if fastq_filepath is None:
        handle_fail(job_type=JobType.CLASSIFICATION, job_id=class_job_id,
                    message="NO FASTQ FILEPATH!".format(fastq_filepath))
        return None

    if not os.path.exists(fastq_filepath):
        handle_fail(job_type=JobType.CLASSIFICATION, job_id=class_job_id,
                    message="JOB FILE {} DOES NOT EXIST!".format(fastq_filepath))
        return None
    return user_job_id, class_job_id, classifier, fastq_filepath


def setup_job_directories(fastq_filepath: str, classifier: str) -> (str, str, str):
    # Fastq file is expected to be located here: /data/jobs/<user_job_id>/<read_type>/simulated.fastq
    base_path = os.path.split(fastq_filepath)[0].replace(config.JOBS_DIR, config.CONTAINER_DATA_BIND)

    # Make new directory in job folder for classifier
    path = os.path.join(base_path, classifier)
    if not os.path.exists(path.replace(config.CONTAINER_DATA_BIND, config.JOBS_DIR)):
        os.mkdir(path.replace(config.CONTAINER_DATA_BIND, config.JOBS_DIR))

    # Initialize path names
    result_filepath = os.path.join(path, "{}.result".format(classifier))
    report_filepath = os.path.join(path, "{}.report".format(classifier))
    input_filepath = fastq_filepath.replace(config.JOBS_DIR, config.CONTAINER_DATA_BIND)
    return result_filepath, report_filepath, input_filepath
