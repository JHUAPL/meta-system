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
from shared.log import logger


def calculate_max_memory_megabytes(sys_mem: type, curr_mem_used: float = 0):
    max_mem_used = curr_mem_used
    try:
        max_mem_used = max(curr_mem_used, sys_mem.used / 1024 / 1024)
    except AttributeError:
        logger.error("SYSTEM MEMORY OBJECT DOES NOT HAVE ATTRIBUTE `USED`. CANNOT COMPUTE MAX MEMORY!")
    return max_mem_used
