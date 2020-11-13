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
import shutil
import unittest
from datetime import datetime
from distutils.dir_util import copy_tree

import pydash
from werkzeug.datastructures import FileStorage
from werkzeug.datastructures import ImmutableMultiDict

from shared.config import config
from system.api.jobs import add_child_job, fastq_validation, tsv_validation
from system.api.jobs import delete_directory
from system.api.jobs import parse_job_payload
from system.api.jobs import save_uploaded_file, save_multiple_files, unzip_multiple_files, validate_files
from system.controllers import simulation_job, user, user_job
from system.models.job_manager import JobType, JobMode


class TestSaveUploadedFile(unittest.TestCase):
    def setUp(self) -> None:
        self.file_storage = FileStorage(open(os.path.join(config.TEST_DATA_DIR, "mock.tsv"), "rb", buffering=0))
        self.time_stamp = datetime(2020, 9, 30).strftime("%Y-%m-%d-%H:%M:%S")

        self.directory = os.path.join(config.TEST_DATA_DIR, "uploads")
        if not os.path.exists(self.directory):
            os.mkdir(self.directory)

        # ERROR TESTING
        self.file_storage_err = FileStorage(
            open(os.path.join(config.TEST_DATA_DIR, "mock_error_test"), "rb", buffering=0))
        self.time_stamp_err = datetime(2020, 10, 1).strftime("%Y-%m-%d-%H:%M:%S")
        self.filename_error = "Filename {} is not allowed".format(self.file_storage.filename)

    def test_save_uploaded_file(self):
        uploaded_file_path = save_uploaded_file(self.file_storage, self.time_stamp, self.directory)
        true_file_path = os.path.join(self.directory, self.time_stamp, os.path.basename(self.file_storage.filename))
        self.assertEqual(uploaded_file_path, true_file_path)
        path_directory_exists = os.path.isdir(os.path.split(uploaded_file_path)[0])
        self.assertEqual(path_directory_exists, True)

        err_output = save_uploaded_file(self.file_storage_err, self.time_stamp_err, self.directory)
        self.assertEqual(err_output, None)

    def tearDown(self):
        if os.path.exists(self.directory):
            shutil.rmtree(self.directory, ignore_errors=True)


class TestSaveMultipleFiles(unittest.TestCase):
    def setUp(self) -> None:
        self.file_storage = FileStorage(open(os.path.join(config.TEST_DATA_DIR, "fastq_good.zip"), "rb", buffering=0))
        self.time_stamp = datetime(2020, 9, 30).strftime("%Y-%m-%d-%H:%M:%S")

        self.directory = os.path.join(config.TEST_DATA_DIR, "multiple_uploads")
        if not os.path.exists(self.directory):
            os.mkdir(self.directory)

        # ERROR TESTING
        self.file_storage_err = FileStorage(
            open(os.path.join(config.TEST_DATA_DIR, "mock_error_test"), "rb", buffering=0))
        self.time_stamp_err = datetime(2020, 10, 1).strftime("%Y-%m-%d-%H:%M:%S")
        self.filename_error = "Filename {} is not allowed".format(self.file_storage.filename)

    def test_save_multiple_files(self):
        uploaded_file_path = save_multiple_files(self.file_storage, self.time_stamp, self.directory)
        true_file_path = os.path.join(self.directory, self.time_stamp, os.path.basename(self.file_storage.filename))
        self.assertEqual(uploaded_file_path, true_file_path)
        path_directory_exists = os.path.isdir(os.path.split(uploaded_file_path)[0])
        self.assertEqual(path_directory_exists, True)

        # ERROR TESTING
        err_output = save_multiple_files(self.file_storage_err, self.time_stamp_err, self.directory)
        self.assertEqual(err_output, None)

    def tearDown(self):
        if os.path.exists(self.directory):
            shutil.rmtree(self.directory, ignore_errors=True)


class TestUnZipMultipleFiles(unittest.TestCase):
    def setUp(self) -> None:
        self.file_storage = FileStorage(open(os.path.join(config.TEST_DATA_DIR, "fastq_good.zip"), "rb", buffering=0))
        self.time_stamp = datetime(2020, 9, 30).strftime("%Y-%m-%d-%H:%M:%S")
        self.simulate = "true"
        self.not_simulate = "false"
        self.classify = "true"
        self.not_classify = "false"

        self.previous_directory = os.path.join(config.TEST_DATA_DIR, "multiple_uploads")
        if not os.path.exists(self.previous_directory):
            os.mkdir(self.previous_directory)

        self.final_directory = os.path.join(config.TEST_DATA_DIR, "zip_dir")
        if not os.path.exists(self.final_directory):
            os.mkdir(self.final_directory)

        self.true_file_path = [
            os.path.join(self.final_directory, self.time_stamp, os.path.basename(self.file_storage.filename),
                         "fastq_good.fastq")]

        # ERROR TESTING
        self.fastq_file_storage_bad_err1 = FileStorage(
            open(os.path.join(config.TEST_DATA_DIR, "fastq_one_bad_err1.zip"), "rb", buffering=0))
        self.tsv_file_storage_bad_err1 = FileStorage(
            open(os.path.join(config.TEST_DATA_DIR, "tsv_one_bad_err1.zip"), "rb", buffering=0))
        self.time_stamp_fastq_bad_err1 = datetime(2020, 10, 7).strftime("%Y-%m-%d-%H:%M:%S")
        self.time_stamp_tsv_bad_err1 = datetime(2020, 10, 8).strftime("%Y-%m-%d-%H:%M:%S")
        self.path_to_zip_fastq_bad_err1 = unzip_multiple_files(self.fastq_file_storage_bad_err1, self.previous_directory,
                                                               self.final_directory, self.time_stamp_fastq_bad_err1, self.simulate, self.not_classify)
        self.path_to_zip_tsv_bad_err1 = unzip_multiple_files(self.tsv_file_storage_bad_err1, self.previous_directory, self.final_directory,
                                                             self.time_stamp_tsv_bad_err1, self.not_simulate, self.classify)
        self.improper_file_type_for_classify = "INCORRECT FILE TYPE UPLOADED, EXPECTING FASTQ FOR CLASSIFY"
        self.improper_file_type_for_simulate = "INCORRECT FILE TYPE UPLOADED, EXPECTING TSV FOR SIMULATE + CLASSIFY"

    def test_unzip_multiple_files(self):
        returned_file_paths = unzip_multiple_files(self.file_storage, self.previous_directory,
                                                   self.final_directory, self.time_stamp, self.not_simulate, self.classify)
        self.assertEqual(returned_file_paths, self.true_file_path)

        # ERROR TESTING
        self.assertEqual(self.path_to_zip_fastq_bad_err1, self.improper_file_type_for_simulate)
        self.assertEqual(self.path_to_zip_tsv_bad_err1, self.improper_file_type_for_classify)

    def tearDown(self):
        if os.path.exists(self.previous_directory):
            shutil.rmtree(self.final_directory, ignore_errors=True)
            shutil.rmtree(self.previous_directory, ignore_errors=True)


class TestValidateMultipleFiles(unittest.TestCase):
    def setUp(self) -> None:
        self.fastq_file_storage_good = FileStorage(
            open(os.path.join(config.TEST_DATA_DIR, "fastq_good.zip"), "rb", buffering=0))
        self.tsv_file_storage_good = FileStorage(
            open(os.path.join(config.TEST_DATA_DIR, "tsv_good.zip"), "rb", buffering=0))
        self.time_stamp_fastq_good = datetime(2020, 9, 30).strftime("%Y-%m-%d-%H:%M:%S")
        self.time_stamp_tsv_good = datetime(2020, 10, 1).strftime("%Y-%m-%d-%H:%M:%S")
        self.simulate = "true"
        self.not_simulate = "false"
        self.classify = "true"
        self.not_classify = "false"

        self.previous_directory = os.path.join(config.TEST_DATA_DIR, "multiple_uploads")
        if not os.path.exists(self.previous_directory):
            os.mkdir(self.previous_directory)

        self.final_directory = os.path.join(config.TEST_DATA_DIR, "zip_dir")
        if not os.path.exists(self.final_directory):
            os.mkdir(self.final_directory)

        self.path_to_zip_fastq_good = unzip_multiple_files(self.fastq_file_storage_good, self.previous_directory,
                                                           self.final_directory, self.time_stamp_fastq_good, self.not_simulate, self.classify)
        self.path_to_zip_tsv_good = unzip_multiple_files(self.tsv_file_storage_good, self.previous_directory,
                                                         self.final_directory, self.time_stamp_tsv_good, self.simulate, self.not_classify)
        self.validation_message_tsv_good = [os.path.basename(''.join(self.path_to_zip_tsv_good)) + " is Valid"]
        self.validation_message_fastq_good = [os.path.basename(''.join(self.path_to_zip_fastq_good)) + " is Valid"]

        # ERROR TESTING 1
        self.fastq_file_storage_bad_err1 = FileStorage(
            open(os.path.join(config.TEST_DATA_DIR, "fastq_one_bad_err1.zip"), "rb", buffering=0))
        self.tsv_file_storage_bad_err1 = FileStorage(
            open(os.path.join(config.TEST_DATA_DIR, "tsv_one_bad_err1.zip"), "rb", buffering=0))
        self.time_stamp_fastq_bad_err1 = datetime(2020, 10, 2).strftime("%Y-%m-%d-%H:%M:%S")
        self.time_stamp_tsv_bad_err1 = datetime(2020, 10, 3).strftime("%Y-%m-%d-%H:%M:%S")

        self.path_to_zip_fastq_bad_err1 = unzip_multiple_files(self.fastq_file_storage_bad_err1, self.previous_directory,
                                                               self.final_directory, self.time_stamp_fastq_bad_err1, self.not_simulate, self.classify)
        self.path_to_zip_tsv_bad_err1 = unzip_multiple_files(self.tsv_file_storage_bad_err1, self.previous_directory,
                                                             self.final_directory, self.time_stamp_tsv_bad_err1, self.simulate, self.not_classify)

        self.validation_message_fastq_bad_err1 = os.path.basename(''.join(self.path_to_zip_fastq_bad_err1[0]) )+ " is NOT IN FASTQ FORMAT: FILE MUST START WITH '@'"
        self.validation_message_tsv_bad_err1 = os.path.basename(''.join(self.path_to_zip_tsv_bad_err1[1])) + " is NOT IN TSV FORMAT: 2ND COLUMN MUST SUM TO 1"

        # ERROR TESTING 2
        self.fastq_file_storage_bad_err2 = FileStorage(open(os.path.join(config.TEST_DATA_DIR, "fastq_one_bad_err2.zip"), "rb", buffering=0))
        self.tsv_file_storage_bad_err2 = FileStorage(open(os.path.join(config.TEST_DATA_DIR, "tsv_one_bad_err2.zip"), "rb", buffering=0))
        self.time_stamp_fastq_bad_err2 = datetime(2020, 10, 4).strftime("%Y-%m-%d-%H:%M:%S")
        self.time_stamp_tsv_bad_err2 = datetime(2020, 10, 5).strftime("%Y-%m-%d-%H:%M:%S")

        self.path_to_zip_fastq_bad_err2 = unzip_multiple_files(self.fastq_file_storage_bad_err2, self.previous_directory,
                                                               self.final_directory, self.time_stamp_fastq_bad_err2, self.not_simulate, self.classify)
        self.path_to_zip_tsv_bad_err2 = unzip_multiple_files(self.tsv_file_storage_bad_err2, self.previous_directory,
                                                             self.final_directory, self.time_stamp_tsv_bad_err2, self.simulate, self.not_classify)

        self.validation_message_fastq_bad_err2 = os.path.basename(''.join(self.path_to_zip_fastq_bad_err2[0]) )+ " is NOT IN FASTQ FORMAT: Line 4 MUST START WITH '+'"
        self.validation_message_tsv_bad_err2 = os.path.basename(''.join(self.path_to_zip_tsv_bad_err2[1])) + " is NOT IN TSV FORMAT: FILE MUST HAVE EXACTLY THREE COLUMNS. ROW 2\n IS MISSING FIELDS"

        # ERROR TESTING 3
        self.fastq_file_storage_bad_err3 = FileStorage(
            open(os.path.join(config.TEST_DATA_DIR, "fastq_one_bad_err3.zip"), "rb", buffering=0))
        self.time_stamp_fastq_bad_err3 = datetime(2020, 10, 6).strftime("%Y-%m-%d-%H:%M:%S")

        self.path_to_zip_fastq_bad_err3 = unzip_multiple_files(self.fastq_file_storage_bad_err3, self.previous_directory,
                                                               self.final_directory, self.time_stamp_fastq_bad_err3, self.not_simulate, self.classify)

        self.validation_message_fastq_bad_err3 = os.path.basename(''.join(self.path_to_zip_fastq_bad_err3[0]) )+ " is NOT IN FASTQ FORMAT: LINE 2 MUST ONLY CONTAIN A,C,G,T, OR N"

        # ERROR TESTING 4
        self.fastq_file_storage_bad_err4 = FileStorage(open(os.path.join(config.TEST_DATA_DIR, "fastq_one_good_two_bad.zip"), "rb", buffering=0))
        self.tsv_file_storage_bad_err4 = FileStorage(open(os.path.join(config.TEST_DATA_DIR, "tsv_one_good_two_bad.zip"), "rb", buffering=0))
        self.time_stamp_fastq_bad_err4 = datetime(2020, 10, 7).strftime("%Y-%m-%d-%H:%M:%S")
        self.time_stamp_tsv_bad_err4 = datetime(2020, 10, 8).strftime("%Y-%m-%d-%H:%M:%S")

        self.path_to_zip_fastq_bad_err4 = unzip_multiple_files(self.fastq_file_storage_bad_err4, self.previous_directory,
                                                               self.final_directory, self.time_stamp_fastq_bad_err4, self.not_simulate, self.classify)
        self.path_to_zip_tsv_bad_err4 = unzip_multiple_files(self.tsv_file_storage_bad_err4, self.previous_directory,
                                                             self.final_directory, self.time_stamp_tsv_bad_err4, self.simulate, self.not_classify)

        self.validation_message_fastq_bad_err4 = [os.path.basename(''.join(self.path_to_zip_fastq_bad_err4[0])) + " is NOT IN FASTQ FORMAT: Line 4 MUST START WITH '+'",
                                                  os.path.basename(''.join(self.path_to_zip_fastq_bad_err4[1]))+ " is Valid",
                                                  os.path.basename(''.join(self.path_to_zip_fastq_bad_err4[2]))+ " is NOT IN FASTQ FORMAT: LINE 2 MUST ONLY CONTAIN A,C,G,T, OR N"]


        self.validation_message_tsv_bad_err4 = [os.path.basename(''.join(self.path_to_zip_tsv_bad_err4[0])) + " is Valid",
                                                os.path.basename(''.join(self.path_to_zip_tsv_bad_err4[1])) + " is NOT IN TSV FORMAT: FILE MUST HAVE EXACTLY THREE COLUMNS. ROW 10\n IS MISSING FIELDS",
                                                os.path.basename(''.join(self.path_to_zip_tsv_bad_err4[2])) + " is NOT IN TSV FORMAT: 2ND COLUMN MUST SUM TO 1"]

    def test_validate_files(self):
        fastq_returned_validation_messages = validate_files(self.path_to_zip_fastq_good)
        tsv_returned_validation_messages = validate_files(self.path_to_zip_tsv_good)
        self.assertEqual(tsv_returned_validation_messages, self.validation_message_tsv_good)
        self.assertEqual(fastq_returned_validation_messages, self.validation_message_fastq_good)

        # ERROR 1
        fastq_returned_validation_messages_err1 = validate_files(self.path_to_zip_fastq_bad_err1)
        tsv_returned_validation_messages_err1 = validate_files(self.path_to_zip_tsv_bad_err1)
        self.assertEqual(fastq_returned_validation_messages_err1[0], self.validation_message_fastq_bad_err1)
        self.assertEqual(tsv_returned_validation_messages_err1[1], self.validation_message_tsv_bad_err1)

        # ERROR 2
        fastq_returned_validation_messages_err2 = validate_files(self.path_to_zip_fastq_bad_err2)
        tsv_returned_validation_messages_err2 = validate_files(self.path_to_zip_tsv_bad_err2)
        self.assertEqual(fastq_returned_validation_messages_err2[0], self.validation_message_fastq_bad_err2)
        self.assertEqual(tsv_returned_validation_messages_err2[1], self.validation_message_tsv_bad_err2)

        # ERROR 3
        fastq_returned_validation_messages_err3 = validate_files(self.path_to_zip_fastq_bad_err3)
        self.assertEqual(fastq_returned_validation_messages_err3[0], self.validation_message_fastq_bad_err3)

        # ERROR 4
        fastq_returned_validation_messages_err4 = validate_files(self.path_to_zip_fastq_bad_err4)
        tsv_returned_validation_messages_err4 = validate_files(self.path_to_zip_tsv_bad_err4)
        self.assertEqual(fastq_returned_validation_messages_err4, self.validation_message_fastq_bad_err4)
        self.assertEqual(tsv_returned_validation_messages_err4, self.validation_message_tsv_bad_err4)

    def tearDown(self):
        if os.path.exists(self.previous_directory):
            shutil.rmtree(self.final_directory, ignore_errors=True)
            shutil.rmtree(self.previous_directory, ignore_errors=True)


class TestDeleteDirectory(unittest.TestCase):
    def setUp(self) -> None:
        self.is_multiple_files_good = "true"
        self.is_multiple_files_bad = "false"

        self.zip_directory = os.path.join(config.TEST_DATA_DIR, "zip_dir", "test_delete_directory")
        if not os.path.exists(self.zip_directory):
            os.makedirs(self.zip_directory)

        self.multiple_directory = os.path.join(config.TEST_DATA_DIR, "multiple_uploads", "test_delete_directory")
        if not os.path.exists(self.multiple_directory):
            os.makedirs(self.multiple_directory)

        self.zip_dir = os.path.join(config.TEST_DATA_DIR, "zip_dir")
        self.multiple_uploads_dir = os.path.join(config.TEST_DATA_DIR, "multiple_uploads")

        self.file_path_fastq_zip = os.path.join(config.TEST_DATA_DIR, "zip_dir",
                                     "test_delete_directory_fastq_zip","fastq.zip/fastq/test_1.fastq")

        copy_tree(os.path.join(config.TEST_DATA_DIR, "test_delete_directory_tsv_upload"), self.multiple_directory)
        copy_tree(os.path.join(config.TEST_DATA_DIR, "test_delete_directory_fastq_upload"), self.multiple_directory)

        copy_tree(os.path.join(config.TEST_DATA_DIR, "test_delete_directory_tsv_zip"), self.zip_directory)
        copy_tree(os.path.join(config.TEST_DATA_DIR, "test_delete_directory_fastq_zip"), self.zip_directory)

        self.directory_message_good = "FILES HAVE BEEN PROPERLY REMOVED"
        self.directory_message_none = "None"
        self.directory_message_bad = "FILENAME LEAD TO FAILED DELETED DIRECTORIES"

    def test_delete_directory(self):
        delete_response_none = delete_directory(self.file_path_fastq_zip, self.is_multiple_files_bad, self.zip_dir, self.multiple_uploads_dir)
        delete_response_bad = delete_directory(None, self.is_multiple_files_bad, self.zip_dir, self.multiple_uploads_dir)
        delete_response_good= delete_directory(self.file_path_fastq_zip, self.is_multiple_files_good, self.zip_dir, self.multiple_uploads_dir)

        self.assertEqual(delete_response_none, self.directory_message_none)
        self.assertEqual(delete_response_bad, self.directory_message_bad)
        self.assertEqual(delete_response_good, self.directory_message_good)

    def tearDown(self):
        if os.path.exists(self.zip_dir) and os.path.exists(self.multiple_uploads_dir):
            shutil.rmtree(self.zip_dir, ignore_errors=True)
            shutil.rmtree(self.multiple_uploads_dir, ignore_errors=True)


class TestParseJobPayload(unittest.TestCase):
    def setUp(self) -> None:
        self.payload_without_readtype = ImmutableMultiDict(
            [('title', 'hello'), ('filePath', '/test.fastq'), ('classifiers', "['centrifuge']")])
        self.payload_with_readtype = ImmutableMultiDict(
            [('title', 'hello'), ('filePath', '/test.fastq'), ('read_types', "['r9']"),
             ('classifiers', "['centrifuge']")])

    def test_parse_job_payload_without_readtypes(self):
        title, filePath, _, classifiers = parse_job_payload(payload=self.payload_without_readtype)
        _, _, read_types, _ = parse_job_payload(payload=self.payload_with_readtype)
        self.assertEqual(title, str(pydash.get(self.payload_without_readtype, "title")))
        self.assertEqual(filePath, str(pydash.get(self.payload_without_readtype, "filePath")))
        self.assertEqual(str(classifiers), str(pydash.get(self.payload_without_readtype, "classifiers")))
        self.assertEqual(str(read_types), str(pydash.get(self.payload_with_readtype, "read_types")))
        return


class TestAddChildJob(unittest.TestCase):
    def setUp(self) -> None:
        # testing with a simulation job
        self.user_id = user.insert(name="Username", email="Usernme@biology.org", user_jobs=[])
        self.payload_example = ImmutableMultiDict(
            [('title', 'hello'), ('filePath', '/mock.tsv'), ('read_types', "['r9']"),
             ('classifiers', "['centrifuge']")])
        self.title, self.filePath, self.read_types, self.classifiers = parse_job_payload(payload=self.payload_example)
        self.user_job_id = user_job.insert(user_id=self.user_id, title=self.title, read_types=self.read_types,
                                           classifiers=self.classifiers, mode=JobMode.SIMULATED_READS)
        self.child_job_id = simulation_job.insert(user_job_id=self.user_job_id, read_type=self.read_types,
                                                  abundance_tsv=os.path.basename(self.filePath),
                                                  number_of_reads=config.DEFAULT_NUM_READS)
        self.job_type = JobType.SIMULATION

    def test_add_child_job(self):
        b_job_inserted, previous_num_child, num_child, job_data = add_child_job(user_job_id=self.user_job_id,
                                                                                child_job_id=self.child_job_id,
                                                                                job_type=self.job_type)
        sim_job_data = pydash.get(job_data, "data")

        self.assertEqual(b_job_inserted, True)
        self.assertEqual(previous_num_child + 1, num_child)
        self.assertEqual(sim_job_data.user_job_id, self.user_job_id)
        return


class TestValidateFastq(unittest.TestCase):
    def setUp(self) -> None:
        self.fastq_path_good = os.path.join(config.TEST_DATA_DIR, "mock.fastq")
        self.fastq_path_bad_err1 = os.path.join(config.TEST_DATA_DIR, "mock_bad_err1.fastq")
        self.fastq_path_bad_err2 = os.path.join(config.TEST_DATA_DIR, "mock_bad_err2.fastq")
        self.fastq_path_bad_err3 = os.path.join(config.TEST_DATA_DIR, "mock_bad_err3.fastq")

        self.valid = "Valid"
        self.invalid_err1 = "NOT IN FASTQ FORMAT: FILE MUST START WITH '@'"
        self.invalid_err2 = "NOT IN FASTQ FORMAT: Line 4 MUST START WITH '+'"
        self.invalid_err3 = "NOT IN FASTQ FORMAT: LINE 2 MUST ONLY CONTAIN A,C,G,T, OR N"

    def test_fastq_validation(self):
        res_good = fastq_validation(fastq_path=self.fastq_path_good)
        self.assertEqual(res_good, self.valid)

        res_bad = fastq_validation(fastq_path=self.fastq_path_bad_err1)
        self.assertEqual(res_bad, self.invalid_err1)

        res_bad = fastq_validation(fastq_path=self.fastq_path_bad_err2)
        self.assertEqual(res_bad, self.invalid_err2)

        res_bad = fastq_validation(fastq_path=self.fastq_path_bad_err3)
        self.assertEqual(res_bad, self.invalid_err3)
        return


class TestValidateTsv(unittest.TestCase):
    def setUp(self) -> None:
        self.tsv_path_good = os.path.join(config.TEST_DATA_DIR, "mock.tsv")
        self.tsv_path_bad_sum1 = os.path.join(config.TEST_DATA_DIR, "mock_bad_err1.tsv")
        self.tsv_path_bad_missing = os.path.join(config.TEST_DATA_DIR, "mock_bad_err2.tsv")

        self.valid = "Valid"
        self.invalid_err1 = "NOT IN TSV FORMAT: 2ND COLUMN MUST SUM TO 1"
        self.invalid_err2 = "NOT IN TSV FORMAT: FILE MUST HAVE EXACTLY THREE COLUMNS. ROW 2 IS MISSING FIELDS"

    def test_tsv_validation(self):
        res_good = tsv_validation(tsv_path=self.tsv_path_good)
        self.assertEqual(res_good, self.valid)

        res_bad = tsv_validation(tsv_path=self.tsv_path_bad_sum1)
        self.assertEqual(res_bad, self.invalid_err1)

        res_bad = tsv_validation(tsv_path=self.tsv_path_bad_missing)
        self.assertEqual(res_bad.replace("\n", ""), self.invalid_err2)
        return


if __name__ == '_main_':
    unittest.main()
