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
from system.utils.security import str_normalize_attr


def get_read_types() -> (list, dict):
    """
    Read data read_types from read_types.yaml and create objects into namedtuples
    """
    yaml_file = open(config.READTYPES_PATH, "r")
    read_type_names, read_types_info = get_read_types_parser(yaml_file)
    return read_type_names,read_types_info

def get_read_types_parser(yaml_file):
    info = yaml.load(yaml_file, Loader=yaml.FullLoader)
    read_types_info = dict()
    read_types = namedtuple("read_types", info[next(iter(info))].keys())
    read_type_names = list(info.keys())
    for name, values in info.items():
        values = {k: str_normalize_attr(v) for k, v in values.items()}
        v_read_types = read_types(**values)
        pydash.set_(read_types_info, name, v_read_types)
    return read_type_names, read_types_info