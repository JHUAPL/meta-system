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
import json
import os
import re

import pandas as pd
import pydash
from bson import ObjectId
from flask import Blueprint, send_from_directory

from shared.config import config
from shared.log import logger
from system import FlaskExtensions
from system.controllers import classification_job, simulation_job, user_job
from system.models.metrics import SimulationMetrics, ClassificationMetrics
from system.utils.biology import TaxonomicHierarchy
from system.utils.zip import send_to_zip

results_bp = Blueprint("results", __name__, url_prefix=config.SERVER_API_CHROOT)

mongodb = FlaskExtensions.mongodb


@results_bp.route("/results/orig_abundance_profile/<string:user_job_id>")
def get_original_abundance_profile(user_job_id):
    # Taxid Abundance Organization files: data/jobs/<user_job_id>/*.tsv
    job = user_job.find_by_id(user_job_id=ObjectId(user_job_id))
    if job is None:
        return "{} does not exist!".format(user_job_id), 501
    tsv_name = pydash.get(job, "abundance_tsv", None)
    if tsv_name is not None:
        path = os.path.join(config.JOBS_DIR, user_job_id, tsv_name)
        abundance_df = get_result_dataframe(path, ["taxid", "abundance", "val"])
        if abundance_df is None:
            return "No abundance profile tsv file for {}!".format(user_job_id), 501
        parsed_abundance_json = abundance_df.to_dict("records")
        return json.dumps(parsed_abundance_json), 200
    else:
        logger.error("No abundance TSV found for job {}".format(user_job_id))
        return None, 501


@results_bp.route(
    "/results/computation/simulation/<string:metric>/<string:user_job_id>/<string:read_type>",
    methods=["GET"])
def get_cpu_time_simulation(metric, user_job_id, read_type):
    try:
        SimulationMetrics(metric)
    except ValueError:
        return None, 501
    data = simulation_job.find_specific_job(user_job_id=ObjectId(user_job_id), read_type=read_type)
    res = {metric: pydash.get(data, metric, None)}
    return json.dumps(res), 200


@results_bp.route(
    "/results/computation/classification/<string:metric>/<string:user_job_id>/<string:read_type>/<string:classifier>",
    methods=["GET"])
def get_computational_performance_simulated(metric, user_job_id, read_type, classifier):
    try:
        ClassificationMetrics(metric)
    except ValueError:
        return None, 501

    data = classification_job.find_specific_job(user_job_id=ObjectId(user_job_id), read_type=read_type,
                                                classifier=classifier)
    res = {metric: pydash.get(data, metric, None)}
    return json.dumps(res), 200


@results_bp.route(
    "/results/computation/classification/<string:metric>/<string:user_job_id>/<string:classifier>",
    methods=["GET"])
def get_computational_performance_real(metric, user_job_id, classifier):
    try:
        ClassificationMetrics(metric)
    except ValueError:
        return None, 501

    data = classification_job.find_specific_job(user_job_id=ObjectId(user_job_id), classifier=classifier)
    res = {metric: pydash.get(data, metric, None)}
    return json.dumps(res), 200


@results_bp.route("/results/<string:user_job_id>/<string:read_type>/compare", methods=["GET"])
def get_results_for_user_job_and_read_type(user_job_id, read_type):
    # Eval tsv: data/jobs/<user_job_id>/<read_type>/compare
    path = os.path.join(config.JOBS_DIR, user_job_id, read_type, "eval", "eval.tsv")
    eval_df = get_result_dataframe(path)
    if eval_df is None:
        return "No evaluation TSV file found!", 501
    eval_json = eval_df.to_dict("records")
    return json.dumps(eval_json), 200


@results_bp.route("/results/<string:user_job_id>/inclusion", methods=["GET"])
def get_classifier_rank_abu_taxid_org_inclusion_real(user_job_id):
    # classifier_rank_abu_taxid_org_inclusion tsv:
    #   /data/jobs/<user_job_id>/eval/classifier_rank_abu_taxid_org_inclusion.tsv
    path = os.path.join(config.JOBS_DIR, user_job_id, "eval", "classifier_rank_abu_taxid_org_inclusion.tsv")
    eval_df = get_result_dataframe(path, ['classifier', 'rank', 'abundance', 'taxid', 'name', 'classifier_inclusion'])
    eval_df['classifier_inclusion'] = eval_df['classifier_inclusion'].str.split(',')
    eval_df['classifier_count'] = eval_df['classifier_inclusion'].str.len()
    if eval_df is None:
        return "No evaluation TSV file found!", 501
    eval_json = eval_df.to_dict("records")
    return json.dumps(eval_json), 200


@results_bp.route("/results/<string:user_job_id>/<string:read_type>/inclusion", methods=["GET"])
def get_classifier_rank_abu_taxid_org_inclusion_simulated(user_job_id, read_type):
    # classifier_rank_abu_taxid_org_inclusion tsv:
    #   /data/jobs/<user_job_id>/<read_type>/eval/classifier_rank_abu_taxid_org_inclusion.tsv
    path = os.path.join(config.JOBS_DIR, user_job_id, read_type, "eval", "classifier_rank_abu_taxid_org_inclusion.tsv")
    eval_df = get_result_dataframe(path, ['classifier', 'rank', 'abundance', 'taxid', 'name', 'classifier_inclusion'])
    eval_df['classifier_inclusion'] = eval_df['classifier_inclusion'].str.split(',')
    eval_df['classifier_count'] = eval_df['classifier_inclusion'].str.len()
    if eval_df is None:
        return "No evaluation TSV file found!", 501
    eval_json = eval_df.to_dict("records")
    return json.dumps(eval_json), 200


@results_bp.route("/results/<string:user_job_id>/<string:read_type>/<string:classifier>", methods=["GET"])
def get_results_for_user_job_and_read_type_and_classifier(user_job_id, read_type, classifier):
    # Report files: data/jobs/<user_job_id>/<read_type>/results/*.parsed_<classifier>
    path = os.path.join(config.JOBS_DIR, user_job_id, read_type, "results", "*.parsed_{}".format(classifier))
    parsed_report_df = get_result_dataframe(path, ["taxid", "abundance"])
    if parsed_report_df is None:
        return "No report file for {} {}!".format(classifier, user_job_id), 501
    parsed_report_json = parsed_report_df.to_dict("records")
    return json.dumps(parsed_report_json), 200


@results_bp.route("/results/taxid_abu_org/<string:user_job_id>/<string:read_type>/<string:classifier>/<string:rank>",
                  methods=["GET"])
def get_results_for_taxid_abu_org_by_rank(user_job_id, read_type, classifier, rank):
    # Taxid Abundance Organization files: data/jobs/<user_job_id>/<read_type>/eval/tmp/parsed_<classifier>/taxid_abu_org-<rank>.tsv
    path = os.path.join(config.JOBS_DIR, user_job_id, read_type, "eval", "tmp", "parsed_{}_dir".format(classifier),
                        "taxid_abu_org-{}.tsv".format(rank))
    taxid_abu_org_df = get_result_dataframe(path, ["abundance", "taxid", "name"])
    if taxid_abu_org_df is None:
        return "No Tax ID Abundance Organization file for {} {} {}!".format(rank, read_type, user_job_id), 501
    taxid_abu_org_json = taxid_abu_org_df.to_dict("records")
    return json.dumps(taxid_abu_org_json), 200


@results_bp.route("/results/taxid_abu_org/<string:user_job_id>/<string:classifier>",
                  methods=["GET"])
def get_hierarchical_taxid_real(user_job_id, classifier):
    # -------------------------------- Get result taxid abundance hierarchy --------------------------------
    path = os.path.join(config.JOBS_DIR, user_job_id, "eval", "tmp", "parsed_{}_dir".format(classifier),
                        "taxid.abu.ts.padded")

    if not os.path.exists(path):
        logger.warning("taxid.abu.ts.padded not found! Using taxid.abu.ts")
        path = os.path.join(config.JOBS_DIR, user_job_id, "eval", "tmp", "parsed_{}_dir".format(classifier),
                            "taxid.abu.ts")

    taxid_abu_ts_df = get_result_dataframe(path, ["taxid", "abundance", "hierarchy"])
    if taxid_abu_ts_df is None:
        return "No taxid.abu.ts file for {} {} {}!".format(user_job_id, classifier), 501

    # -------------------------------- Build hierarchy --------------------------------
    hierarchy_col = taxid_abu_ts_df["hierarchy"].tolist()
    abundance_col = taxid_abu_ts_df["abundance"].tolist()

    tree = dict()
    if len(hierarchy_col) > 0:
        logger.info("BUILDING HIERARCHY FOR {} TAXONOMIC IDs".format(len(hierarchy_col)))
        tree = build_hierarchy(hierarchy_list=hierarchy_col, abundance_list=abundance_col)
    else:
        logger.warning("taxid.abu.ts IS EMPTY!")
    return json.dumps(tree), 200


@results_bp.route("/results/taxid_abu_org/<string:user_job_id>/<string:read_type>/<string:classifier>",
                  methods=["GET"])
def get_hierarchical_taxid_simulated(user_job_id, read_type, classifier):
    # -------------------------------- Get result taxid abundance hierarchy --------------------------------
    path = os.path.join(config.JOBS_DIR, user_job_id, read_type, "eval", "tmp", "parsed_{}_dir".format(classifier),
                        "taxid.abu.ts.padded")
    if not os.path.exists(path):
        logger.warning("taxid.abu.ts.padded not found! Using taxid.abu.ts")
        path = os.path.join(config.JOBS_DIR, user_job_id, read_type, "eval", "tmp", "parsed_{}_dir".format(classifier),
                            "taxid.abu.ts")

    taxid_abu_ts_df = get_result_dataframe(path, ["taxid", "abundance", "hierarchy"])
    if taxid_abu_ts_df is None:
        return "No taxid.abu.ts file for {} {} {}!".format(user_job_id, read_type, classifier), 501

    # -------------------------------- Get baseline taxid abundance hierarchy --------------------------------
    path = os.path.join(config.JOBS_DIR, user_job_id, read_type, "eval", "tmp", "BASELINE1.tsv_dir",
                        "taxid.abu.ts.padded")
    if not os.path.exists(path):
        logger.warning("taxid.abu.ts.padded not found for Baseline! Using taxid.abu.ts")
        path = os.path.join(config.JOBS_DIR, user_job_id, read_type, "eval", "tmp", "BASELINE1.tsv_dir", 'taxid.abu.ts')

    taxid_abu_baseline_ts_df = get_result_dataframe(path, ["taxid", "abundance", "hierarchy"])
    taxid_abu_baseline_ts_df["abundance"] = 0

    # ---------------------------- Merge the baseline and classifier abundance ts files ----------------------------
    taxid_abu_ts_df = pd.concat([taxid_abu_ts_df, taxid_abu_baseline_ts_df]).reset_index().drop_duplicates(
        subset=["taxid"], keep="first")
    pd.options.display.max_colwidth = 10000

    # -------------------------------- Build hierarchy --------------------------------
    hierarchy_col = taxid_abu_ts_df["hierarchy"].tolist()
    abundance_col = taxid_abu_ts_df["abundance"].tolist()

    tree = dict()
    if len(hierarchy_col) > 0:
        logger.info("BUILDING HIERARCHY FOR {} TAXONOMIC IDs".format(len(hierarchy_col)))
        tree = build_hierarchy(hierarchy_list=hierarchy_col, abundance_list=abundance_col)
    else:
        logger.warning("taxid.abu.ts IS EMPTY!")
    return json.dumps(tree), 200


def build_hierarchy(hierarchy_list: list, abundance_list: list):
    pattern = re.compile(r"(\d+);([/\-A-Z\w\s.\[\]=]+)\(?([\w\s]+)\)?")
    hier_per_taxid = []
    for i, h in enumerate(hierarchy_list):
        try:
            res = re.findall(pattern, h)
            hier_per_taxid.append(res)
        except TypeError as e:
            logger.warning("Cannot parse {} in hierarchical taxid. Line {}.".format(h, i))

    proper_taxid = False

    while not proper_taxid:  # find root node
        try:
            taxid, name, rank = hier_per_taxid[0][0]
            proper_taxid = True
        except IndexError:
            hier_per_taxid.pop(0)

    root_node = TaxonomicHierarchy.Node(taxid=taxid, name=name, rank=rank, abundance=None)
    th = build_tree(root_node=root_node, hier_per_taxid=hier_per_taxid, abundance_list=abundance_list)

    return th.to_dict()


def build_tree(root_node: TaxonomicHierarchy.Node, hier_per_taxid: list, abundance_list: list):
    th = TaxonomicHierarchy(root=root_node)

    # Build entire tree
    for i, hier in enumerate(hier_per_taxid):
        hier.pop(0)  # remove root node, assumes root node is first in list
        parent_node = root_node
        for n, h in enumerate(hier):
            taxid, name, rank = h
            if rank == "subspecies":
                rank = "strain"
            if rank in ["superkingdom", "phylum", "class", "order", "family", "genus", "species",
                        "strain"]:  # ignore no rank for now so that all ranks will consistent across nesting levels
                if h == hier[-1]:  # if last element in list
                    node = TaxonomicHierarchy.Node(taxid=taxid, name=name, rank=rank, abundance=abundance_list[i])
                    th.add_child_to_tree(parent=parent_node, child=node)
                else:
                    node = TaxonomicHierarchy.Node(taxid=taxid, name=name, rank=rank, abundance=None)
                    th.add_child_to_tree(parent=parent_node, child=node)
                    parent_node = node
    return th


def get_result_dataframe(path: str, columns: list or None = None):
    try:
        filepath = glob.glob(path)[0]
        if not filepath:
            logger.error("No {} found!".format(path))
            return None
    except IndexError:
        return None
    if columns is not None:
        return pd.read_csv(filepath, sep="\t", encoding="utf-8", names=columns)
    else:
        return pd.read_csv(filepath, sep="\t", encoding="utf-8")


@results_bp.route("/results/download/<string:user_job_id>/<string:filename>",
                  methods=["GET"])  # download relevant job files
def download(user_job_id, filename):
    """
    # Accepts job id and downloads the results files related to it
    # :param: user_job_id to download files for
    # :param: path of the filename to download
    # :return: Success of moving the files to a zip download folder
    """
    try:
        logger.info("DOWNLOAD JOBS REQUEST SUBMITTED FOR USER JOB {}".format(user_job_id))

        user_job_data = user_job.find_by_id(user_job_id=ObjectId(user_job_id))
        read_types = [""]  # list with empty quotes is needed to ensure the classify only jobs work
        if "read_types" in user_job_data:  # classify only jobs will not have a specified read_type
            read_types = pydash.get(user_job_data, "read_types")
        classifiers = pydash.get(user_job_data, "classifiers")

        # Make zip
        zip_loc = os.path.join(config.DATA_DIR, "jobs", user_job_id)
        list_of_files = list_files_for_download(read_types=read_types, classifiers=classifiers, job_path=zip_loc)
        send_to_zip(base_path=zip_loc, list_of_files=list_of_files, outfile=filename)

        if not os.path.exists(os.path.join(zip_loc, filename)):
            return "File does not exist", 400
        logger.info("SUCCESSFULLY MOVED JOB {} TO ZIP FOR DOWNLOAD".format(user_job_id))
        logger.info("ABOUT TO ATTEMPT SEND RESULTS.ZIP TO FRONT END...")

        return send_from_directory(directory=zip_loc, filename=filename, as_attachment=True)

    except Exception as e:
        logger.warning("DOWNLOAD JOB {} REQUEST FAILED".format(user_job_id))
        return "DOWNLOAD JOB {} REQUEST FAILED".format(user_job_id), 501


def list_files_for_download(read_types: list, classifiers: list, job_path: str) -> list:
    """
    Download the existing UserJob by placing the relevant files in a zip folder.
    :param read_types:
    :param classifiers:
    :param job_path:
    :return: List of files to include in download
    """

    # list files in zip folder
    list_of_files = []  # list of files to add to zip, with relative paths to user_job_path
    try:
        for r in read_types:
            for c in classifiers:
                list_of_files.append(os.path.join(r, c, c + ".report"))  # get .report file

                list_of_files.append(os.path.join(r, c, c + ".result"))  # get .results file

            # inclusion and eval tsvs are only outputted per read_type
            if not ("" in read_types):  # Classify only jobs do not have eval.tsv
                list_of_files.append(os.path.join(r, "eval", "eval.tsv"))  # get eval.tsv file

            list_of_files.append(
                os.path.join(r, "eval", "classifier_rank_abu_taxid_org_inclusion.tsv"))  # get inclusion.tsv file

            # results folder contains parsed classifier results
            parsed_results = os.listdir(os.path.join(job_path, r, "results"))
            for parsed in parsed_results:  # add file structure to each parsed results file
                list_of_files.append(os.path.join(r, "results", parsed))

    except Exception as e:
        logger.warning("ERROR COMPILING RESULTS IN ZIP FOLDER")
        return list_of_files

    return list_of_files
