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

from tests.system import test_job_queue_manager, test_simulate, test_evaluate, test_classify
from tests.system import test_job_queue_manager, test_simulate, test_evaluate, test_classify
from tests.system.api import test_info, test_jobs, test_results
from tests.system.api import test_info, test_jobs, test_results
from tests.system.controllers import test_classification_job, test_controllers, test_evaluation_job, test_user_job, \
    test_user, test_simulation_job, test_job_queue
from tests.system.controllers import test_classification_job, test_controllers, test_evaluation_job, test_user_job, \
    test_user, test_simulation_job, test_job_queue
from tests.system.metric.classification import test_computational_resources
from tests.system.metric.classification import test_computational_resources
from tests.system.utils import test_zip, test_security, test_encoder, test_biology, test_biocontainers
from tests.system.utils import test_zip, test_security, test_encoder, test_biology, test_biocontainers

quick_tests = [
    # api
    test_info,
    test_jobs,
    test_results,
    # controllers
    test_classification_job,
    test_controllers,
    test_evaluation_job,
    test_job_queue,
    test_simulation_job,
    test_user,
    test_user_job,
    # metric
    test_computational_resources,
    test_biocontainers,
    test_biology,
    test_encoder,
    test_security,
    test_zip,
    # component
    test_job_queue_manager
]

slow_tests = [
    # component
    test_classify,
    test_evaluate,
    test_simulate
]
