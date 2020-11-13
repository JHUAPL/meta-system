#  **********************************************************************
#  Copyright (C) 2020 Johns Hopkins University Applied Physics Laboratory
#
#  All Rights Reserved.
#  For any other permission, please contact the Legal Office at JHU/APL.
#  **********************************************************************

import unittest


# To run tests: `python -m unittest discover -s tests -v`
# To view coverage: `coverage run --source=system/ -m unittest`
#                   `coverage report`
#                   `coverage html` --> open `meta_system/htmlcov/index.html`


class TestStringMethods(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def test_upper(self):
        self.assertEqual("foo".upper(), "FOO")

    def test_isupper(self):
        self.assertTrue("FOO".isupper())
        self.assertFalse("Foo".isupper())

    def test_split(self):
        s = "hello world"
        self.assertEqual(s.split(), ["hello", "world"])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

    def tearDown(self) -> None:
        pass


if __name__ == "__main__":
    unittest.main()
