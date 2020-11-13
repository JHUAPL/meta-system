#  **********************************************************************
#  Copyright (C) 2020 Johns Hopkins University Applied Physics Laboratory
#
#  All Rights Reserved.
#  For any other permission, please contact the Legal Office at JHU/APL.
#  **********************************************************************

import unittest

from system.utils.security import allowed_file, str_normalize_attr


class TestAllowedFile(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def test_allowed_file(self):
        self.assertEqual(allowed_file(filename="foo.fastq"), True)
        self.assertEqual(allowed_file(filename="foo.fasta"), True)
        self.assertEqual(allowed_file(filename="foo.tsv"), True)
        self.assertEqual(allowed_file(filename="foo.zip"), True)

        self.assertEqual(allowed_file(filename="foo.jpeg"), False)
        self.assertEqual(allowed_file(filename="foobar"), False)
        return


class TestStrNormalize(unittest.TestCase):

    def setUp(self) -> None:
        self.attr_str = "a\u0062c"
        self.attr_list = list(["\u007Be", "f", "g"])
        pass

    def test_str_normalize_attr(self):
        # check isinstance for
        res_str = str_normalize_attr(attr=self.attr_str)
        self.assertEqual(res_str, "abc")

        res_list = str_normalize_attr(attr=self.attr_list)
        self.assertEqual(res_list, ["{e", "f", "g"])
        return


if __name__ == '_main_':
    unittest.main()
