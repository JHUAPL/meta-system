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
import posixpath
from typing import Set

from pydantic import BaseSettings, validator
from uritools import uricompose


class MetaConfiguration(BaseSettings):
    # Helpers
    THIS_DIR: str = os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(__file__))))
    ROOT_DIR: str = os.path.normpath(os.path.join(THIS_DIR, os.pardir))

    # Server Settings
    DEBUG: bool = True
    SERVER_BIND: str = "0.0.0.0"
    SERVER_PORT: str = 5000
    SERVER_API_CHROOT: str = "/api"
    CLIENT_PORT: str = 8080

    # Directories
    STATIC_DIR: str = os.path.join(ROOT_DIR, "app", "dist")

    # Data Directories
    DATA_DIR: str = os.path.join(ROOT_DIR, "data")
    LOCAL_FASTQ_DIR: str = os.path.join(DATA_DIR, "fastq")
    JOBS_DIR: str = os.path.join(DATA_DIR, "jobs")
    UPLOAD_DIR: str = os.path.join(DATA_DIR, "uploads")
    MULTIPLE_DIR: str = os.path.join(DATA_DIR, "multiple_uploads")
    ZIP_DIR: str = os.path.join(DATA_DIR, "zip_dir")
    DOCKER_DIR: str = os.path.join(DATA_DIR, "docker")

    # Test Directories
    TEST_DIR: str = os.path.join(ROOT_DIR, "tests")
    TEST_DATA_DIR: str = os.path.join(TEST_DIR, "data")

    # Configure META simulation
    ALLOWED_EXTENSIONS: Set[str] = {"fasta", "fastq", "tsv", "zip"}
    META_SIMULATOR_IMAGE_NAME: str = "meta_simulator:latest"
    DEFAULT_NUM_READS: int = 100000
    NUM_SIM_THREADS: int = 18
    SIMULATED_FASTQ_NAME: str = "simulated.fastq"

    # Configure META evaluation
    NUM_EVAL_THREADS: int = 24

    # Configure Biocontainers info and database paths
    BIOCONTAINERS_YAML_NAME: str = "biocontainers.yaml"  # for full system
    # BIOCONTAINERS_YAML_NAME: str = "biocontainers_mini.yaml"  # for demo system
    BIOCONTAINER_DB_DIR: str = ""
    BIOCONTAINERS_PATH: str = os.path.join(ROOT_DIR, BIOCONTAINERS_YAML_NAME)

    # Configure Read types info
    READTYPES_PATH: str = os.path.join(ROOT_DIR, "read_types.yaml")

    # Configure custom database build files (Optional, only if building custom databases using META system)
    CUSTOM_GENOMIC_FNA_FILEPATH: str = ""
    CUSTOM_PROTEIN_FAA_FILEPATH: str = ""

    # Configure container mounting paths
    CONTAINER_DB_BIND: str = "/db"
    CONTAINER_DATA_BIND: str = "/data"

    # Configure MongoDB
    MONGO_HOST: str = "localhost"
    MONGO_PORT: int = 27017
    MONGO_DBNAME: str = "meta"
    MONGO_URI: str = uricompose("mongodb", host=MONGO_HOST, port=MONGO_PORT, path=posixpath.join("/", MONGO_DBNAME))

    # Validate and Create Missing Directories
    @validator("LOCAL_FASTQ_DIR", "JOBS_DIR", "UPLOAD_DIR", "MULTIPLE_DIR", "ZIP_DIR", "DOCKER_DIR")
    def inherits_data_dir_path(cls, v, values):  # noqa: C901
        data_dir = values["DATA_DIR"]
        is_child_of_data_dir = data_dir == os.path.commonprefix([v, data_dir])
        r_value = v
        if not is_child_of_data_dir:
            last_dir_part = os.path.basename(os.path.normpath(v))
            r_value = os.path.join(data_dir, last_dir_part)
        # Create Directories
        os.makedirs(r_value, mode=0o775, exist_ok=True)
        return r_value

    # Validate and Adjust MongoDB URI
    @validator("MONGO_URI")
    def dynamic_mongo_uri(cls, v, values):  # noqa: C901
        return uricompose("mongodb", host=values["MONGO_HOST"], port=values["MONGO_PORT"], path=posixpath.join("/", values["MONGO_DBNAME"]))

    # Configure Pydantic Environment Prefix
    class Config(object):
        env_prefix = "META_"


# Importable Instance...
config = MetaConfiguration()
