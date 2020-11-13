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

import glob
import os
import shlex
import subprocess
import time
from datetime import datetime
from enum import Enum

import pydash
from bson import ObjectId

from shared.config import config
from shared.log import logger
from system.controllers import evaluation_job, user_job
from system.models.job_manager import JobMode, JobStatus, JobType
from system.utils.job_failure import handle_fail

metrics_root_dir = os.path.join(config.ROOT_DIR, "system", "metrics", "evaluation")


def run_evaluation_job(job: dict):
    # -------------------- Parse input --------------------
    user_job_id = pydash.get(job, "user_job_id")
    eval_job_id = pydash.get(job, "_id")
    if eval_job_id is None:
        logger.warning("JOB ID NOT INCLUDED!")
        return

    read_type = pydash.get(job, "read_type", None)

    evaluation_job.update_status(obj_id=eval_job_id, new_status=str(JobStatus.PROCESSING))

    user_job_data = user_job.find_by_id(user_job_id=user_job_id)
    if user_job_data is None:
        handle_fail(job_type=JobType.EVALUATION, job_id=eval_job_id, message="User Job Data not provided!")
        return

    job_mode = pydash.get(user_job_data, "mode", None)
    if job_mode is None:
        handle_fail(job_type=JobType.EVALUATION, job_id=eval_job_id, message="Job mode not provided!")
    try:
        job_mode_enum = JobMode(job_mode)
    except ValueError as e:
        job_mode_enum = JobMode.SIMULATED_READS  # use Simulated mode as default
        handle_fail(job_type=JobType.EVALUATION, job_id=eval_job_id, message=e)

    if job_mode_enum == JobMode.SIMULATED_READS:
        # eval_job_dir: data/jobs/<user_job_id>/<read_type>
        eval_job_dir = os.path.join(config.JOBS_DIR, str(user_job_id), read_type)
    elif job_mode_enum == JobMode.REAL_READS:
        # eval_job_dir: data/jobs/<user_job_id>
        eval_job_dir = os.path.join(config.JOBS_DIR, str(user_job_id))
    else:
        handle_fail(job_type=JobType.EVALUATION, job_id=eval_job_id, message="Invalid Job Mode!")
        return

    classifiers = pydash.get(user_job_data, "classifiers", [])
    logger.info("RUNNING EVALUATION FOR USER JOB {} ({})".format(str(user_job_id), classifiers))

    t_dur, t_dur_cpu = evaluate(job_dir=eval_job_dir, classifiers=classifiers, eval_job_id=eval_job_id,
                                user_job_id=user_job_id, job_mode_enum=job_mode_enum)

    logger.info("EVALUATION FINISHED FOR USER JOB {} IN {} ({} CPU TIME)".format(
        str(user_job_id), str(t_dur), str(t_dur_cpu)))
    return


def evaluate(job_dir: str, classifiers: list, eval_job_id: ObjectId, user_job_id: ObjectId, job_mode_enum: Enum) -> (
        datetime or None, datetime or None):
    t_start = datetime.now()
    t_start_cpu = datetime.fromtimestamp(time.process_time())

    eval_dir = os.path.join(job_dir, "eval")
    if not os.path.exists(eval_dir):
        os.mkdir(eval_dir)

    # -------------------- Parse reports --------------------
    parsed_path = parse_reports(classifiers=classifiers, job_dir=job_dir, eval_job_id=eval_job_id)

    # -------------------- Compare --------------------
    # Construct command
    if job_mode_enum == JobMode.SIMULATED_READS:

        # Truth file path (-b): data/jobs/<user_job_id>/*.tsv
        # Assume first file in glob is the baseline abundance tsv file
        truth_file = glob.glob(os.path.join(job_dir, os.pardir, "*.tsv"))[0]
        if not os.path.exists(truth_file):
            handle_fail(job_type=JobType.EVALUATION, job_id=eval_job_id,
                        message="NO ABUNDANCE PROFILE TSV {}!".format(truth_file))
            return

        metacompare_bin = os.path.join(metrics_root_dir, "compare", "metacompare.sh")
        if not os.path.exists(metacompare_bin):
            handle_fail(job_type=JobType.EVALUATION, job_id=eval_job_id,
                        message="NO COMPARE SCRIPT {}!".format(metacompare_bin))
            return

        # Command: metacompare.sh -b {} -i {} -o {} -t {}
        # Parsed path (-i): data/jobs/<user_job_id>/<read_type>/results
        # Output dir (-o): data/jobs/<user_job_id>/<read_type>/eval
        cmd = "{} -b {} -i {} -o {} -t {}".format(metacompare_bin, truth_file, parsed_path, eval_dir,
                                                  config.NUM_EVAL_THREADS)

    elif job_mode_enum == JobMode.REAL_READS:
        metacompare_bin = os.path.join(metrics_root_dir, "compare", "metacompare_realdata.sh")
        if not os.path.exists(metacompare_bin):
            handle_fail(job_type=JobType.EVALUATION, job_id=eval_job_id,
                        message="NO COMPARE SCRIPT {}!".format(metacompare_bin))
            return None, None

        # Command: metacompare_realdata.sh -i {} -o {} -t {}
        # Parsed path (-i): data/jobs/<user_job_id>/<read_type>/results
        # Output dir (-o): data/jobs/<user_job_id>/eval
        cmd = "{} -i {} -o {} -t {}".format(metacompare_bin, parsed_path, eval_dir,
                                            config.NUM_EVAL_THREADS)

    else:
        handle_fail(job_type=JobType.EVALUATION, job_id=eval_job_id, message="Invalid Job Mode!")
        return None, None

    split_cmd = shlex.split(cmd)
    subprocess.run(split_cmd)  # Make sure it is chmod +x
    logger.info("RUNNING METACOMPARE.SH")

    t_end_cpu = datetime.fromtimestamp(time.process_time())
    t_dur_cpu = t_end_cpu - t_start_cpu

    t_end = datetime.now()
    t_dur = t_end - t_start

    # Update performance metrics for job.
    evaluation_job.update_cpu_time(obj_id=eval_job_id, time=t_dur_cpu.total_seconds())
    evaluation_job.update_wall_clock_time(obj_id=eval_job_id, time=t_dur.total_seconds())
    evaluation_job.update_status(obj_id=eval_job_id, new_status=str(JobStatus.COMPLETED))
    user_job.update_completion_time(obj_id=user_job_id, time=t_end)
    return t_dur, t_dur_cpu


def parse_reports(classifiers: list, job_dir: str, eval_job_id: ObjectId) -> str:
    # Parsed paths (-o): <eval_job_dir>/results
    parsed_path = os.path.join(job_dir, "results")
    if not os.path.exists(parsed_path):
        os.mkdir(parsed_path)

    logger.info("Attempting to download taxdump")
    taxdump_bin = os.path.join(metrics_root_dir, "parsers", "download_taxdump.sh")
    try:
        subprocess.run(taxdump_bin, capture_output=False, check=True)
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
        logger.error("Failed to download taxdump", exc_info=e)
        return parsed_path

    for c in classifiers:
        # Report paths (-i): <eval_job_dir>/<classifier>/<classifier>.report
        report_path = os.path.join(job_dir, c, "{}.report".format(c))
        if not os.path.exists(report_path):
            handle_fail(job_type=JobType.EVALUATION, job_id=eval_job_id,
                        message="NO REPORT FILE {}!".format(report_path))
            continue

        parser_bin = os.path.join(metrics_root_dir, "parsers", "parse_{}.sh".format(c))
        if not os.path.exists(parser_bin):
            handle_fail(job_type=JobType.EVALUATION, job_id=eval_job_id,
                        message="NO PARSING SCRIPT {}!".format(parser_bin))
            continue

        # Command: parse_kraken.sh -i {} -o {}
        cmd = "{} -i {} -o {}".format(parser_bin, report_path, parsed_path)
        split_cmd = shlex.split(cmd)
        logger.info("PARSING {} REPORT".format(c))

        # find meta_system/system/metrics/evaluation -type f -iname "*.sh" -exec chmod +x {} \;
        subprocess.run(split_cmd)  # Make sure it is chmod +x
    return parsed_path
