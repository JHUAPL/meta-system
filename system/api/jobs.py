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

import ast
import json
import os
import shlex
import shutil
import zipfile
from datetime import datetime

import pydash
import sh
from bson import ObjectId
from flask import Blueprint, request
from pymodm import connect

from shared.config import config
from shared.log import logger
from system.controllers import classification_job, evaluation_job, job_queue, simulation_job, user, user_job
from system.extensions import FlaskExtensions
from system.job_queue_manager import push_job, set_job_manager_running_status, restart_job_queue_watchdog
from system.models.job_manager import JobType, JobMode
from system.utils.biocontainers import get_biocontainers, kill_running_container
from system.utils.encoder import json_encoder
from system.utils.readtypes import get_read_types
from system.utils.security import allowed_file

logger.info("{}".format(config.MONGO_URI))
connect(config.MONGO_URI)

jobs_bp = Blueprint("jobs", __name__, url_prefix=config.SERVER_API_CHROOT)

mongodb = FlaskExtensions.mongodb


@jobs_bp.route("/jobs/file_upload/files", methods=["POST", "GET"])
def get_dropzone_files():
    payload = request.form
    sentFile = pydash.get(payload, "upload")
    multiple_files = pydash.get(payload, "multiple")
    simulate_bool = pydash.get(payload, "simulate")
    classify_bool = pydash.get(payload, "classify")

    if request.files.get("fastq") is not None:
        file_upload = request.files.get("fastq")
        if os.path.splitext(file_upload.filename)[1] == ".zip" and multiple_files =="false":
            logger.info("INCORRECT FILE TYPE: CANNOT BE A ZIP")
            validation_messages = ["INCORRECT FILE TYPE: CANNOT BE A ZIP"]
            return json.dumps(dict(messages=validation_messages))

        if os.path.splitext(file_upload.filename)[1] == ".tsv":
            logger.info("INCORRECT FILE TYPE: MUST BE A FASTQ")
            validation_messages = ["INCORRECT FILE TYPE: MUST BE A FASTQ"]
            return json.dumps(dict(messages=validation_messages))
    else:
        file_upload = request.files.get("tsv")
        if os.path.splitext(file_upload.filename)[1] == ".zip" and multiple_files =="false":
            logger.info("INCORRECT FILE TYPE: CANNOT BE A ZIP")
            validation_messages = ["INCORRECT FILE TYPE: CANNOT BE A ZIP"]
            return json.dumps(dict(messages=validation_messages))

        if os.path.splitext(file_upload.filename)[1] == ".fastq":
            logger.info("INCORRECT FILE TYPE: MUST BE A TSV")
            validation_messages = ["INCORRECT FILE TYPE: MUST BE A TSV"]
            return json.dumps(dict(messages=validation_messages))

    if multiple_files == "true" and (os.path.splitext(file_upload.filename)[1] == ".tsv" or os.path.splitext(file_upload.filename)[1] == ".fastq"):
        logger.info("MUST BE A ZIP FILE!")
        validation_messages = ["MUST BE A ZIP FILE!"]
        return json.dumps(dict(messages=validation_messages))

    if multiple_files == "true":
        file_upload = request.files.get("zip")
        unique_code = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
        final_path = unzip_multiple_files(file_upload, config.MULTIPLE_DIR, config.ZIP_DIR, unique_code, simulate_bool, classify_bool)

        if final_path[0:9] == "INCORRECT":
            validation_messages = [final_path]
            return json.dumps(dict(messages=validation_messages))

        final_relative_path = list()

        for path in final_path :
            final_relative_path.append(path.split(config.ZIP_DIR)[1])
        validation_messages = validate_files(final_path)
        all_files_valid = list()

        for message in validation_messages:
            if message[-5:] == "Valid":
                all_files_valid.append(True)
            else:
                all_files_valid.append(False)
        if all(all_files_valid) is True:
            validation_messages = ["Valid"]

        return json.dumps(dict(paths=final_relative_path, messages=validation_messages)), 200

    if sentFile is False:
        logger.warning("File Not Found")
        return "File Not Found", 501
    else:
        logger.info("FILE {} RECEIVED".format(file_upload.filename))
        unique_code = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
        path = save_uploaded_file(file_upload, unique_code, config.UPLOAD_DIR)
        sent_path = path.split(config.UPLOAD_DIR)[1]
        validation_messages = validate_files(path.strip('][').split(","))
        return json.dumps(dict(paths=sent_path, messages=validation_messages)), 200


@jobs_bp.route("/jobs/submit_simulation", methods=["POST"])
def submit_simulation():
    """
    Accepts job FormData payload of the form:
    abundance_profile_tsv (file) - [byte stream] abundance profile in the form of tsv
    read types - [List(str)] list of read types to simulate
    classifiers - [List(str)] list of classifiers to run with system
    user_id - [str] user ID
    :return: list of jobs created [List(Dict)]
    """
    payload = request.form
    title, abundance_profile_tsv, read_types, classifiers = parse_job_payload(payload=payload)
    total_jobs = abundance_profile_tsv.strip('][').split(",")

    # Create UserJob
    user_id = user.insert(name="Username", email="Username@biology.org",
                          user_jobs=[])  # TODO: eventually should be actual user
    title = str(pydash.get(payload, "title"))
    multiple_files = pydash.get(payload, "multiple_files")
    for jobs in total_jobs:
        read_types = ast.literal_eval(pydash.get(payload, "read_types"))
        read_types = [r for r in read_types if r in get_read_types()[0]]
        if len(read_types) < 1:
            logger.error("No valid read types provided!")
            return "No valid read types provided!", 501

        classifiers = ast.literal_eval(pydash.get(payload, "classifiers"))
        classifiers = [c for c in classifiers if c in get_biocontainers()[0]]
        if len(classifiers) < 1:
            logger.error("No valid classifiers provided!")
            return "No valid classifiers provided!", 501

            # Create UserJob
        user_job_id = user_job.insert(user_id=user_id, title=title, read_types=read_types,
                                      classifiers=classifiers, mode=JobMode.SIMULATED_READS)

        tsv_filename = save_file(jobs, user_job_id, multiple_files)
        user_job.update_abundance_tsv(obj_id=user_job_id, abundance_tsv=os.path.basename(tsv_filename))

        if tsv_filename is not None:
            job_pipeline = []

            # Create SimulationJobs
            for r in read_types:
                simulation_job_id = simulation_job.insert(user_job_id=user_job_id, read_type=r,
                                                          abundance_tsv=os.path.basename(tsv_filename),
                                                          number_of_reads=config.DEFAULT_NUM_READS)
                user_job.add_child(obj_id=user_job_id, child_id=simulation_job_id, job_type=JobType.SIMULATION)
                job_queue.insert(job_type=JobType.SIMULATION, job_id=simulation_job_id)
                data = simulation_job.find_by_id(sim_job_id=simulation_job_id)
                data = dict(type=JobType.SIMULATION, data=data)
                push_job(job=data)

                # Create ClassificationJobs per SimulationJob
                path = os.path.join(config.JOBS_DIR, str(user_job_id), r, config.SIMULATED_FASTQ_NAME)
                for c in classifiers:
                    classification_job_id = classification_job.insert(user_job_id=user_job_id, classifier=c,
                                                                      fastq_path=path, read_type=r)
                    user_job.add_child(obj_id=user_job_id, child_id=classification_job_id,
                                       job_type=JobType.CLASSIFICATION)
                    job_queue.insert(job_type=JobType.CLASSIFICATION, job_id=classification_job_id)
                    data = classification_job.find_by_id(class_job_id=classification_job_id)
                    data = dict(type=JobType.CLASSIFICATION, data=data)
                    push_job(job=data)

                # Create EvaluationJob per SimulationJob
                evaluation_job_id = evaluation_job.insert(user_job_id=user_job_id, read_type=r)
                user_job.add_child(obj_id=user_job_id, child_id=evaluation_job_id, job_type=JobType.EVALUATION)
                job_queue.insert(job_type=JobType.EVALUATION, job_id=evaluation_job_id)
                data = evaluation_job.find_by_id(eval_job_id=evaluation_job_id)
                data = dict(type=JobType.EVALUATION, data=data)
                push_job(job=data)

        else:
            logger.error("Abundance profile *.tsv file could not be saved!")
            return "Abundance profile *.tsv file could not be saved!", 501

        res = dict(user_job=user_job, job_pipeline=job_pipeline)

    #delete all files saved excluding those in JOBS_DIR
    delete_directory(total_jobs[0], multiple_files, config.ZIP_DIR, config.MULTIPLE_DIR)
    return json.dumps(res, default=json_encoder), 200


@jobs_bp.route("/jobs/submit_classification", methods=["POST"])
def submit_classification():
    """
    Accepts job FormData payload of the form:
    fastq (file) - [byte stream] sequence profile in the form of fastq
    classifiers - [List(str)] list of classifiers to run with system
    user_id - [str] user ID
    :return: list of jobs created [List(Dict)]
    """
    payload = request.form
    title, fastq, _, classifiers = parse_job_payload(payload=payload)
    total_jobs = fastq.strip('][').split(",")
    user_id = user.insert(name="Username", email="Username@biology.org",
                          user_jobs=[])
    title = str(pydash.get(payload, "title"))
    multiple_files = pydash.get(payload, "multiple_files")

    for jobs in total_jobs:
        classifiers = ast.literal_eval(pydash.get(payload, "classifiers"))
        classifiers = [c for c in classifiers if c in get_biocontainers()[0]]
        if len(classifiers) < 1:
            logger.error("No valid classifers provided!")
            return "No valid read types provided!", 501

        # Create UserJob
        user_job_id = user_job.insert(user_id=user_id, title=title, read_types=None,
                                      classifiers=classifiers,
                                      mode=JobMode.REAL_READS)  # mode1= 'simulated', mode2= 'real'
        fastq_filename = save_file(jobs, user_job_id, multiple_files)

        user_job.update_fastq(obj_id=user_job_id, fastq=os.path.basename(fastq_filename))
        if fastq_filename is not None:
            job_pipeline = []
            # Create ClassificationJobs w/o SimulationJob
            path = os.path.join(config.JOBS_DIR, str(user_job_id), fastq_filename)
            for c in classifiers:
                classification_job_id = classification_job.insert(user_job_id=user_job_id, classifier=c,
                                                                  fastq_path=path)
                user_job.add_child(obj_id=user_job_id, child_id=classification_job_id, job_type=JobType.CLASSIFICATION)
                job_queue.insert(job_type=JobType.CLASSIFICATION, job_id=classification_job_id)
                data = classification_job.find_by_id(class_job_id=classification_job_id)
                data = dict(type=JobType.CLASSIFICATION, data=data)
                push_job(job=data)

            # Create EvaluationJob after all Classification Jobs
            evaluation_job_id = evaluation_job.insert(user_job_id=user_job_id)
            user_job.add_child(obj_id=user_job_id, child_id=evaluation_job_id, job_type=JobType.EVALUATION)
            job_queue.insert(job_type=JobType.EVALUATION, job_id=evaluation_job_id)
            data = evaluation_job.find_by_id(eval_job_id=evaluation_job_id)
            data = dict(type=JobType.EVALUATION, data=data)
            push_job(job=data)
        else:
            logger.error("fastq file could not be saved!")
            return "fastq file could not be saved!", 501

        res = dict(user_job=user_job, job_pipeline=job_pipeline)

    #delete all files saved excluding those in JOBS_DIR
    delete_directory(total_jobs[0], multiple_files, config.ZIP_DIR, config.MULTIPLE_DIR)
    return json.dumps(res, default=json_encoder), 200


def add_child_job(user_job_id: ObjectId, child_job_id: ObjectId, job_type: JobType):
    previous_num_child, num_child = user_job.add_child(obj_id=user_job_id, child_id=child_job_id, job_type=job_type)
    job_queue.insert(job_type=job_type, job_id=child_job_id)

    if job_type == JobType.SIMULATION:
        data = simulation_job.find_by_id(sim_job_id=child_job_id)
    elif job_type == JobType.CLASSIFICATION:
        data = classification_job.find_by_id(class_job_id=child_job_id)
    elif job_type == JobType.EVALUATION:
        data = evaluation_job.find_by_id(eval_job_id=child_job_id)
    else:
        logger.error("Invalid job type {}!".format(job_type))
        return False, previous_num_child, num_child, None

    data = dict(type=job_type, data=data)
    return True, previous_num_child, num_child, data


def parse_job_payload(payload: dict) -> (str, str, list or None, list):
    """
    Parse payload passed to `submit_classification` and `submit_simulation` endpoints
    :param payload:
    :return:
    """
    title = str(pydash.get(payload, "title"))
    file = str(pydash.get(payload, "filePath"))

    read_types = ast.literal_eval(pydash.get(payload, "read_types", "None"))
    if read_types is not None:  # if not None, check if they're valid
        read_types = [r for r in read_types if r in get_read_types()[0]]
        if len(read_types) < 1:
            logger.error("No valid read types provided!")
            return "No valid read types provided!", 501

    classifiers = ast.literal_eval(pydash.get(payload, "classifiers"))
    classifiers = [c for c in classifiers if c in get_biocontainers()[0]]
    if len(classifiers) < 1:
        logger.error("No valid classifiers provided!")
        return "No valid classifiers provided!", 501
    return title, file, read_types, classifiers


def save_file(file, job_id, multiple_files):
    # Save to /data/jobs/<user_job_id>/
    if file is not None:
        filename = os.path.basename(file)
        received_filename = os.path.join(config.JOBS_DIR, str(job_id), filename)
        os.mkdir(os.path.split(received_filename)[0])
        file_path_with_out_slash = file.strip("/")
        if multiple_files == "true":
            previous_path = os.path.join(config.ZIP_DIR, file_path_with_out_slash)
        else:
            previous_path = os.path.join(config.UPLOAD_DIR, file_path_with_out_slash)
        shutil.move(previous_path, received_filename)
        unique_path = previous_path.split(filename)[0]
        if multiple_files != "true":
            os.rmdir(unique_path)  # delete the now empty directiory
    else:
        return None
    return received_filename


def delete_directory(file, multiple_files, zip_directory, uploads_directory):
    if file is not None:
        if multiple_files == "true":
            for directory_name in os.listdir(os.path.join(zip_directory)):
                path_in_zip_directory = os.path.join(zip_directory, directory_name)
                path_in_multiple_directory = os.path.join(uploads_directory, directory_name)
                logger.info(path_in_multiple_directory)
                logger.info(path_in_zip_directory)
                try:
                    if os.path.isdir(path_in_multiple_directory) and os.path.isdir(path_in_zip_directory):
                        shutil.rmtree(path_in_zip_directory)
                        shutil.rmtree(path_in_multiple_directory)
                        logger.info("FILES HAVE BEEN PROPERLY REMOVED")
                        return "FILES HAVE BEEN PROPERLY REMOVED"
                except Exception as e:
                    logger.error("FAILED TO PROPERLY REMOVE FILES")
                    return "FAILED TO PROPERLY REMOVE FILES"
        else:
            return "None"
    else:
        logger.error("FILENAME LEAD TO FAILED DELETED DIRECTORIES")
        return "FILENAME LEAD TO FAILED DELETED DIRECTORIES"
    return None


def save_uploaded_file(file, time_stamp, directory):
    if file is not None and allowed_file(file.filename):
        filename = os.path.basename(file.filename)
        file.stream.seek(0)  # point to beginning of file stream
        uploaded_file = os.path.join(directory, time_stamp, filename)
        os.mkdir(os.path.split(uploaded_file)[0])
        file.save(uploaded_file)
    else:
        logger.error("Filename {} is not allowed".format(file.filename))
        return None
    return uploaded_file


def save_multiple_files(file, time_stamp, directory):
    if file is not None and allowed_file(file.filename):
        filename = os.path.basename(file.filename)
        file.stream.seek(0)  # point to beginning of file stream
        uploaded_file = os.path.join(directory, time_stamp, filename)
        os.mkdir(os.path.split(uploaded_file)[0])
        file.save(uploaded_file)
    else:
        logger.error("Filename {} is not allowed".format(file.filename))
        return None
    return uploaded_file


def unzip_multiple_files(file_upload, previous_directory, final_directory, unique_code, simulate_bool, classify_bool):
    logger.info("FILE {} RECEIVED".format(file_upload.filename))
    path_to_zip = save_multiple_files(file_upload, unique_code, previous_directory)
    filename = os.path.basename(file_upload.filename)
    file_paths = list()
    final_path_location = os.path.join(final_directory, unique_code, filename)
    with zipfile.ZipFile(path_to_zip, 'r') as zip_ref:
        zip_ref.extractall(final_path_location)
        filenames_info = zip_ref.infolist()

        for data in filenames_info:
            if os.path.splitext(data.filename)[1] == ".tsv" and simulate_bool == "false":
                logger.info("INCORRECT FILE TYPE UPLOADED, EXPECTING FASTQ FOR CLASSIFY")
                return "INCORRECT FILE TYPE UPLOADED, EXPECTING FASTQ FOR CLASSIFY"
            if os.path.splitext(data.filename)[1] == ".fastq" and classify_bool == "false":
                logger.info("INCORRECT FILE TYPE UPLOADED, EXPECTING TSV FOR SIMULATE + CLASSIFY")
                return "INCORRECT FILE TYPE UPLOADED, EXPECTING TSV FOR SIMULATE + CLASSIFY"

            if not(data.is_dir()) and len(data.filename.split('._')) < 2 and (os.path.splitext(data.filename)[1] == ".tsv" or os.path.splitext(data.filename)[1] == ".fastq"):
                file_paths.append(os.path.join(final_directory, unique_code, os.path.basename(path_to_zip), data.filename))
    return file_paths


def validate_files(zipped_paths):
    validation_checks = list()
    for path in zipped_paths:
        if os.path.splitext(path)[1] == ".tsv":
            validation_checks.append(os.path.basename(path) + " is " + tsv_validation(path))
        else:
            validation_checks.append(os.path.basename(path) + " is " + fastq_validation(path))
    return validation_checks


def tsv_validation(tsv_path):
    # Check if abundance profile sums to 1.00
    FIRST_VALIDATION = "'{{sum+=$2}} END{{printf sum}}' {}".format(tsv_path)
    SECOND_VALIDATION = "'{{print NF}}' {}".format(tsv_path)
    THIRD_VALIDATION = "'NF!=3 {{print NR}}' {}".format(tsv_path)
    sort = "-nu"
    head = "-n 1"
    v1 = float(sh.awk(shlex.split(FIRST_VALIDATION)))
    v2 = float(sh.head(sh.sort(sh.awk(shlex.split(SECOND_VALIDATION)), sort), head))
    v3 = sh.awk(shlex.split(THIRD_VALIDATION))

    if v3 != '' or v2 != 3:
        logger.warning("NOT IN TSV FORMAT: FILE MUST HAVE EXACTLY THREE COLUMNS. ROW {} IS MISSING "
                       "FIELDS".format(v3))
        return "NOT IN TSV FORMAT: FILE MUST HAVE EXACTLY THREE COLUMNS. ROW {} IS MISSING FIELDS".format(v3)

    logger.info("ABUNDANCE PROFILE SUMS TO {}".format(v1))
    if v1 != 1:
        logger.warning("NOT IN TSV FORMAT: 2ND COLUMN MUST SUM TO 1")
        return "NOT IN TSV FORMAT: 2ND COLUMN MUST SUM TO 1"

    logger.info("TSV IS IN PROPER FORMAT")
    return "Valid"


def fastq_validation(fastq_path):
    # ONLY looking at first 4 lines
    FIRST_VALIDATION = "NR==1 {}".format(fastq_path)
    SECOND_VALIDATION = "NR==3 {}".format(fastq_path)
    CUT = "-c1"
    THIRD_VALIDATION = "NR==2 {}".format(fastq_path)
    allowed = "[A\n|G\n|T\n|C\n|N\n]"

    v1 = str(sh.cut(sh.awk(shlex.split(FIRST_VALIDATION)), CUT))
    v2 = str(sh.cut(sh.awk(shlex.split(SECOND_VALIDATION)), CUT))
    v3 = all(char in allowed for char in str(sh.awk(shlex.split(THIRD_VALIDATION))))

    if (v1 != '@\n'):
        logger.info("NOT IN FASTQ FORMAT: FILE MUST START WITH '@'")
        return "NOT IN FASTQ FORMAT: FILE MUST START WITH '@'"
    if (v2 != '+\n'):
        logger.info("NOT IN FASTQ FORMAT: Line 4 MUST START WITH '+'")
        return "NOT IN FASTQ FORMAT: Line 4 MUST START WITH '+'"
    if (v3 is False):
        logger.info("NOT IN FASTQ FORMAT: LINE 2 MUST ONLY CONTAIN A,C,G,T, OR N")
        return "NOT IN FASTQ FORMAT: LINE 2 MUST ONLY CONTAIN A,C,G,T, OR N"

    logger.info("FASTQ IS IN PROPER FORMAT")
    return "Valid"


@jobs_bp.route("/jobs/all", methods=["GET"])  # see all pending jobs
def get_jobs():
    res = user_job.find_all(as_json=True)
    return json.dumps(res), 200


@jobs_bp.route("/jobs/unhidden", methods=["GET"])  # see unhidden pending jobs
def get_unhidden_jobs():
    res = user_job.find_unhidden_jobs(as_json=True)
    return json.dumps(res), 200


@jobs_bp.route("/jobs/hidden", methods=["GET"])  # see hidden pending jobs
def get_hidden_jobs():
    res = user_job.find_hidden_jobs(as_json=True)
    return json.dumps(res), 200


@jobs_bp.route("/jobs/hide/<string:user_job_id>", methods=["POST"])  # see hide job status
def hide_jobs(user_job_id):
    """
    Accepts job id:
    param - Job id
    :return:
    """
    hide_success = user_job.hide_job(obj_id=ObjectId(user_job_id))
    if hide_success:
        logger.info("Successfully hid job {}".format(user_job_id))
        return "Successfully hid job {}".format(user_job_id), 200
    else:
        logger.warning("Unsuccessfully hid job {}".format(user_job_id))
        return "Unsuccessfully hid job {}".format(user_job_id), 501


@jobs_bp.route("/jobs/unhide/<string:user_job_id>", methods=["POST"])  # see hide job status
def unhide_jobs(user_job_id):
    """
    Accepts job id:
    param - Job id
    :return:
    """
    hide_success = not (user_job.unhide_job(obj_id=ObjectId(user_job_id)))
    if not hide_success:
        logger.info("Successfully hid job {}".format(user_job_id))
        return "Successfully hid job {}".format(user_job_id), 200
    else:
        logger.warning("Unsuccessfully hid job {}".format(user_job_id))
        return "Unsuccessfully hid job {}".format(user_job_id), 501


@jobs_bp.route("/jobs/cancel/<string:user_job_id>", methods=["POST"])  # cancel a job
def cancel(user_job_id):
    """
    Accepts job id and cancels it:
    :param: user_job_id of jobs to cancel
    :return: Success of cancel action
    """
    try:
        logger.info("CANCEL JOBS REQUEST SUBMITTED FOR USER JOB {}".format(user_job_id))
        b_job_in_progress, container_id = user_job.cancel_job(obj_id=ObjectId(user_job_id))

        if container_id is not None:
            if kill_running_container(container_id):
                logger.info("SUCCESSFULLY KILLED DOCKER {}".format(container_id))

        # job manager is free to process more jobs now
        if b_job_in_progress:  # if cancelled job was currently being processed
            set_job_manager_running_status(is_running=False)  # make job manager available for new jobs
            restart_job_queue_watchdog()  # restart job queue after killing the process
        logger.info("SUCCESSFULLY CANCELLED JOB {}".format(user_job_id))
        return "SUCCESSFULLY CANCELLED JOB {}".format(user_job_id), 200
    except Exception as e:
        logger.warning("CANCEL JOB {} REQUEST FAILED".format(user_job_id))
        logger.error(repr(e))
        return "CANCEL JOB {} REQUEST FAILED".format(user_job_id), 501

@jobs_bp.route("/jobs/delete/<string:user_job_id>", methods=["POST"])  # delete a job
def delete(user_job_id):
    """
    Accepts job id and deltes it:
    :param: user_job_id of jobs to delete
    :return: Success of deleted action
    """
    delete_success = False
    try:
        logger.info("DELETE JOBS REQUEST SUBMITTED FOR USER JOB {}".format(user_job_id))
        user_job_document = user_job.delete_job(ObjectId(user_job_id))
        user_job_directory = os.path.join(config.JOBS_DIR, str(user_job_document["_id"]))

        if os.path.isdir(user_job_directory):
            shutil.rmtree(user_job_directory, ignore_errors=True)
            delete_success = True
        if delete_success :
            logger.info("SUCCESSFULLY DELETED JOB {}".format(user_job_id))
            return "SUCCESSFULLY DELETED JOB {}".format(user_job_id), 200
        else:
            logger.info("UNSUCCESSFULLY DELETED JOB {}".format(user_job_id))
            return "UNSUCCESSFULLY DELETED JOB {}".format(user_job_id), 501

    except Exception as e:
        logger.warning("DELETE JOB {} REQUEST FAILED".format(user_job_id))
        logger.error(repr(e))
        return "DELETE JOB {} REQUEST FAILED".format(user_job_id), 501

