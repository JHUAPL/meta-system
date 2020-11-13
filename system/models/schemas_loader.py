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

from enum import Enum

from system.models.schemas import User, UserJob, SimulationJob, ClassificationJob, EvaluationJob, Classifier, JobQueue


class SchemaLoader(Enum):
    USER = User
    USER_JOB = UserJob
    SIMULATION_JOB = SimulationJob
    CLASSIFICATION_JOB = ClassificationJob
    EVALUATION_JOB = EvaluationJob
    CLASSIFIER = Classifier
    JOB_QUEUE = JobQueue

    @staticmethod
    def get_queryset(collection: Enum):
        model_class = collection.value
        return model_class.objects.get_queryset()

    @staticmethod
    def get_model(collection: Enum):
        model_class = collection.value
        return model_class.objects.model
