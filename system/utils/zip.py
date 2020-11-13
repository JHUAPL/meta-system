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
from zipfile import ZipFile

from shared.log import logger


def send_to_zip(base_path: str, list_of_files: list, outfile: str) -> bool:
    """
    Places a list of files in a zip folder.
    :param base_path: The path all of the files stem from, and where the output zip will go
    :param list_of_files: The list of the all the files, including paths relative to base path,
    that should be included in the zipped folder
    :param outfile: the name of what the zipped folder should be
    :return: true if the zip folder was successfully made
    """
    try:
        zip_loc = os.path.join(base_path, outfile)
        with ZipFile(zip_loc, "w") as zip_obj:
            for fname in list_of_files:
                full_path = os.path.join(base_path, fname)
                if not (os.path.isfile(full_path)):
                    logger.warning("OUTPUT FILE: " + full_path + " NOT FOUND")
                else:
                    zip_obj.write(full_path, fname)

    except Exception as e:
        logger.warning("ERROR COMPILING RESULTS IN ZIP FOLDER")
        return False

    return True
