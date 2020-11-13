#  **********************************************************************
#  Copyright (C) 2020 Johns Hopkins University Applied Physics Laboratory
#
#  All Rights Reserved.
#  For any other permission, please contact the Legal Office at JHU/APL.
#  **********************************************************************

import unittest

import pymongo
from pymodm import connect

from system.controllers.controllers import *
from system.models.schemas_loader import SchemaLoader


class TestControllers(unittest.TestCase):
    mongo_uri = "mongodb://localhost:27017/"

    def setUp(self) -> None:
        user1 = {"name": 'HanSolo', "email": 'han@federation.com'}
        user2 = {"name": 'Chewy', "email": 'chewy@federation.com'}
        user3 = {"name": 'Leia', "email": 'leia@federation.com'}

        self.user_list = [user1, user2, user3]
        self.user_names = ['HanSolo', 'Chewy', 'Leia']
        self.as_json = False  # tests do not work with returns as_json

        # Create a user
        model = SchemaLoader.get_model(SchemaLoader.USER)
        query_set = SchemaLoader.get_queryset(SchemaLoader.USER)
        new_data = []
        for d in self.user_list:
            new_data.append(model.from_document(d))
        query_set.bulk_create(new_data)

        self.my_client = pymongo.MongoClient(self.mongo_uri)
        self.db_name = "TestMETA"
        self.db = self.my_client[self.db_name]
        connect(self.mongo_uri + self.db_name)  # Connect to MongoDB

    def tearDown(self) -> None:
        col_list = self.db.list_collection_names()
        for col in col_list:
            self.db.drop_collection(col)

    # Count users in collection
    def test_count(self):
        # self.assertEqual(count(SchemaLoader.USER), len(self.user_list))
        pass

    # Get all documents in collection
    def test_find_all(self):
        find_result = find_all(SchemaLoader.USER, self.as_json)
        if self.as_json:
            self.assertEqual(len(find_result), len(self.user_list))
        else:
            for res in find_result:
                self.assertIn(res.name, self.user_names)

    # Get document specified by {key: value} pair
    def test_find_by_key_value(self):
        result = find_by_key_value(collection=SchemaLoader.USER, key="email", value="leia@federation.com",
                                   as_json=self.as_json)
        if self.as_json:
            self.assertEqual(result,
                             '{"name":"Leia","email":"leia@federation.com","_id":"5e7298e75001ba5baf4cfb8c"}')
        else:
            self.assertEqual(result[0].name, 'Leia')

    # Insert a single document into collection
    def test_update_by_id(self):
        result = find_by_key_value(collection=SchemaLoader.USER, key="email", value="leia@federation.com",
                                   as_json=self.as_json)
        update_by_id(collection=SchemaLoader.USER, obj_id=result[0]._id, key="email", value="leiasolo@federation.com")
        result = find_by_key_value(collection=SchemaLoader.USER, key="name", value="Leia", as_json=self.as_json)
        if self.as_json:
            self.assertEqual(result['email'], 'leiasolo@federation.com')
        else:
            self.assertEqual(result[0].email, "leiasolo@federation.com")

    # Insert a single document into collection
    def test_insert_one(self):
        user_to_insert = {"name": 'Luke', "email": 'skywalker@federation.com'}
        insert_one(collection=SchemaLoader.USER, data=user_to_insert)
        find_result = find_by_key_value(collection=SchemaLoader.USER, key="email", value="skywalker@federation.com",
                                        as_json=self.as_json)
        if self.as_json:
            self.assertEqual(find_result['name'], 'Luke')
        else:
            self.assertEqual(find_result[0].name, 'Luke')

    # Delete document specified by {key: value} pair
    def test_delete_by_key_value(self):
        result = find_by_key_value(collection=SchemaLoader.USER, key="email", value="leia@federation.com",
                                   as_json=self.as_json)
        self.assertEqual(result[0].name, "Leia")
        self.assertEqual(count(SchemaLoader.USER), len(self.user_list))

        delete_by_key_value(collection=SchemaLoader.USER, key="email", value="leia@federation.com")
        self.assertEqual(count(SchemaLoader.USER), len(self.user_list) - 1)


if __name__ == '__main__':
    unittest.main()
