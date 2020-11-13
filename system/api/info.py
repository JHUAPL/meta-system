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

import json

from flask import Blueprint

from shared.config import config
from system.extensions import FlaskExtensions
from system.utils.biocontainers import get_biocontainers
from system.utils.readtypes import get_read_types

info_bp = Blueprint("info", __name__, url_prefix=config.SERVER_API_CHROOT)

mongodb = FlaskExtensions.mongodb


@info_bp.route("/info/classifiers", methods=["GET"])
def get_classifiers():
    _, classifiers_info = get_biocontainers()
    classifier_links = get_classifiers_links(classifiers_info)
    res = json.dumps(dict(data=classifier_links))
    return res, 200

def get_classifiers_links(classifier_info):
    data = []
    for k, v in classifier_info.items():
        data.append(dict(name=k, link=v.link))
    return data

@info_bp.route("/info/classifiers_only", methods=["GET"])
def get_classifiersOnly():
    classifier_names, _ = get_biocontainers()
    names = get_classifiers_name(classifier_names)
    res = json.dumps(names)
    return res, 200

def get_classifiers_name(classifier_names):
    res = dict(data=classifier_names)
    return res


@info_bp.route("/info/read_types", methods=["GET"])
def get_read_type():
    _, read_types_info = get_read_types()
    read_type_links = get_read_types_links(read_types_info)
    res = json.dumps(dict(data=read_type_links))
    return res, 200

def get_read_types_links(read_types_info):
    data = []
    for k, v in read_types_info.items():
        data.append(dict(name=k, prodlink=v.producturl, simlink=v.simurl))
    return data


@info_bp.route("/info/read_types_only", methods=["GET"])
def get_read_types_only():
    read_type_names, _ = get_read_types()
    names = get_read_type_names(read_type_names)
    res = json.dumps(names)
    return res, 200

def get_read_type_names(read_type_names):
    res = dict(data=read_type_names)
    return res
