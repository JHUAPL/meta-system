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

from collections import namedtuple

import pydash
import yaml

from shared.config import config
from shared.log import logger
from system.extensions import DockerClient
from system.utils.security import str_normalize_attr

docker_client = DockerClient().get_client()


def parse_container_command(command, result_file, report_file, input_file):
    return command \
        .replace("{{VAR_CONTAINER_DB}}", config.CONTAINER_DB_BIND) \
        .replace("{{VAR_RESULT_FILEPATH}}", result_file) \
        .replace("{{VAR_REPORT_FILEPATH}}", report_file) \
        .replace("{{VAR_SEQUENCE_FILEPATH}}", input_file) \
        .replace("{{VAR_GENOMIC_FNA_FILEPATH}}", config.CUSTOM_GENOMIC_FNA_FILEPATH) \
        .replace("{{VAR_PROTEIN_FAA_FILEPATH}}", config.CUSTOM_PROTEIN_FAA_FILEPATH)


def get_biocontainers() -> (list, dict):
    """
    Read data classifiers from metaclassifiers.json and create objects into namedtuples
    :return:
    """
    yaml_file = open(config.BIOCONTAINERS_PATH, "r")
    biocontainers_names, biocontainers_info = get_biocontainers_parser(yaml_file)
    logger.info("AVAILABLE BIOCONTAINERS: {}".format(biocontainers_names))
    return biocontainers_names, biocontainers_info


def get_biocontainers_parser(yaml_file):
    data = yaml.load(yaml_file, Loader=yaml.FullLoader)
    Biocontainer = namedtuple("Biocontainer", data[next(iter(data))].keys())  # get keys of sub dict
    biocontainers_info = dict()
    biocontainers_names = list(data.keys())

    for name, values in data.items():
        values = {k: str_normalize_attr(v) for k, v in values.items()}  # sanitize dictionary
        v_Biocontainer = Biocontainer(**values)
        pydash.set_(biocontainers_info, name, v_Biocontainer)

    return biocontainers_names, biocontainers_info


def kill_running_container(container_id: str) -> bool:
    success = False
    try:
        if container_id is not None:
            job_container = docker_client.containers.get(container_id)
            job_container.kill()
            job_container.remove(v=True, force=True)
            success = True
    except Exception as e:
        logger.error(repr(e))
    return success
