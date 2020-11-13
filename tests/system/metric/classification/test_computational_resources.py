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
import unittest
from collections import namedtuple

from system.metrics.classification.computational_resources import calculate_max_memory_megabytes


class TestMaxMemoryComputation(unittest.TestCase):

    def setUp(self):
        MemObject = namedtuple("MemObject", ["used"])
        MemObjectBad = namedtuple("MemObjectBad", ["foobar"])

        self.memory_object = MemObject(used=17560248320)
        self.memory_object_megabytes = 16746.7578125  # 17560248320 / 1024 / 1024 = 16746.7578125

        self.memory_object_bad = MemObjectBad(foobar=17560248320)

    def test_calculate_max_memory_megabytes_1(self):
        current_memory_megabytes = 8471822991.36
        true_max_memory = current_memory_megabytes
        returned_max_memory = calculate_max_memory_megabytes(sys_mem=self.memory_object,
                                                             curr_mem_used=current_memory_megabytes)
        self.assertEquals(returned_max_memory, true_max_memory)

    def test_calculate_max_memory_megabytes_2(self):
        current_memory_megabytes = 4134.390625
        true_max_memory = self.memory_object_megabytes
        returned_max_memory = calculate_max_memory_megabytes(sys_mem=self.memory_object,
                                                             curr_mem_used=current_memory_megabytes)
        self.assertEquals(returned_max_memory, true_max_memory)

    def test_calculate_max_memory_raise_exception(self):
        current_memory_megabytes = 4134.390625
        true_max_memory = current_memory_megabytes
        returned_max_memory = calculate_max_memory_megabytes(sys_mem=self.memory_object_bad,
                                                             curr_mem_used=current_memory_megabytes)
        self.assertEquals(returned_max_memory, true_max_memory)

