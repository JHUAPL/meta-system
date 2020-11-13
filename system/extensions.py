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

import docker
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_pymongo import PyMongo

from system.models.job_manager import JobManager


class FlaskExtensions:
    bcrypt = Bcrypt()
    jwt = JWTManager()
    mongodb = PyMongo()
    mail = Mail()
    cors = CORS()


class DockerClient:  # FIXME: This doesn't work
    docker_client = docker.from_env()

    def __init___(self):
        if self.docker_client is None:
            self.docker_client = docker.from_env()

    def get_client(self):
        return self.docker_client


class JobManagerClient:  # FIXME: This doesn't work
    job_manager = None

    def __init__(self):
        if self.job_manager is None:
            self.job_manager = JobManager()

    @staticmethod
    def get_client():
        return JobManagerClient.job_manager

    @staticmethod
    def get_running_status():
        return JobManagerClient.job_manager.running

    @staticmethod
    def set_running_status(val: bool):
        JobManagerClient.job_manager.running = val
