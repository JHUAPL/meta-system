#  **********************************************************************
#  Copyright (C) 2020 Johns Hopkins University Applied Physics Laboratory
#
#  All Rights Reserved.
#  For any other permission, please contact the Legal Office at JHU/APL.
#  **********************************************************************
import json
import unittest
from datetime import datetime

from bson import ObjectId

from system.utils.encoder import json_encoder


class TestJsonEncoder(unittest.TestCase):
    def setUp(self) -> None:
        self.datetime = datetime(2020, 5, 19)
        self.object_id = ObjectId("5ebc5e844e1ddf4d7e3de2fc")
        self.data = dict(datetime=self.datetime, id=self.object_id, info="more info",
                         nested_data=dict(datetime=self.datetime, id=self.object_id))
        self.encoded_data = '{"datetime": "2020-05-19 00:00:00", ' \
                            '"id": "5ebc5e844e1ddf4d7e3de2fc", ' \
                            '"info": "more info", ' \
                            '"nested_data": ' \
                            '{"datetime": "2020-05-19 00:00:00", ' \
                            '"id": "5ebc5e844e1ddf4d7e3de2fc"}}'

    def test_json_encoder(self):
        res = json_encoder(o=self.datetime)
        self.assertEqual(res, str(self.datetime))

        res = json_encoder(o=self.object_id)
        self.assertEqual(res, str(self.object_id))
        return

    def test_json_dumps_with_encoder(self):
        res = json.dumps(self.data, default=json_encoder)
        self.assertEqual(res, self.encoded_data)


if __name__ == '_main_':
    unittest.main()
