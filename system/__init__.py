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

from flask import Flask

from shared.config import config
from shared.log import logger
from system.extensions import FlaskExtensions, JobManagerClient, DockerClient
from system.job_queue_manager import job_queue_watchdog

cors = FlaskExtensions.cors
mail = FlaskExtensions.mail
mongodb = FlaskExtensions.mongodb
jwt = FlaskExtensions.jwt
bcrypt = FlaskExtensions.bcrypt


class FlaskApp(object):

    def __init__(self):
        self.app = Flask(__name__, static_folder=config.STATIC_DIR, static_url_path="")
        self.app.config.update(config.dict())

        bcrypt.init_app(self.app)
        jwt.init_app(self.app)
        mongodb.init_app(self.app)
        mail.init_app(self.app)
        cors.init_app(self.app)

        DockerClient()
        JobManagerClient()
        job_queue_watchdog()

        self.register_routes()

    def register_routes(self):
        from system.api.web import web_bp
        self.app.register_blueprint(web_bp)

        from system.api.info import info_bp
        self.app.register_blueprint(info_bp)

        from system.api.database import database_bp
        self.app.register_blueprint(database_bp)

        from system.api.jobs import jobs_bp
        self.app.register_blueprint(jobs_bp)

        from system.api.results import results_bp
        self.app.register_blueprint(results_bp)
