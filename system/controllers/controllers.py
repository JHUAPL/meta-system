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

from datetime import datetime
from enum import Enum

from bson import ObjectId

from shared.log import logger
from system.models.schemas_loader import SchemaLoader

 
def count(collection: Enum) -> int:
    """
    Returns the count of all documents in the collection.
    :param collection: Name of collection for query
    :return: Value of count
    """
    query_set = SchemaLoader.get_queryset(collection) if isinstance(
        collection, SchemaLoader) else None
    if not query_set:  # invalid model error log
        logger.log("Invalid model")

    try:
        return query_set.count()
    except Exception as e:
        logger.error(repr(e))
        return -1


def find_all(collection: Enum, as_json: bool = False) -> str or dict:
    """
    Returns all documents in the collection, as JSON if applicable.
    :param collection: Name of collection for query
    :param as_json: Flag to signify if collection should be returned in JSON format
    :return: All documents in collection
    """
    query_set = SchemaLoader.get_queryset(collection) if isinstance(
        collection, SchemaLoader) else None
    if not query_set:  # invalid model error log
        logger.error("Invalid model")

    try:
        result = query_set.all()
        # return each as a json if desired
        return list(map(lambda d: d.as_json() if as_json else d, result))
    except Exception as e:
        logger.error(repr(e))
        return None


def find_by_id(collection: Enum, obj_id: ObjectId, as_json: bool = False) -> str or dict:
    """
    Returns all documents in the collection, as JSON if applicable.
    :param obj_id: ID of document to find
    :param collection: Name of collection for query
    :param as_json: Flag to signify if collection should be returned in JSON format
    :return: All documents in collection
    """
    query_set = SchemaLoader.get_queryset(collection) if isinstance(
        collection, SchemaLoader) else None

    if not query_set:  # invalid model error log
        logger.error("Invalid model")
    if not isinstance(obj_id, ObjectId):  # check to make sure id is an ObjectId
        logger.error("Invalid ID")

    try:
        # get docs with {key: value} pair in collection
        docs = query_set.get({"_id": obj_id})
        return docs.as_json() if as_json else docs  # return doc as a json if desired
    except Exception as e:
        logger.error(e)
        return None


def find_by_key_value(collection: Enum, key: str, value, as_json: bool = False) -> str or dict:
    """
    Filter collection by {key: value} pair
    :param key: The key to search for in a collection
    :param value: The desired value of key in searching collection
    :param collection: Name of collection for query
    :param as_json: Flag to signify if collection should be returned in JSON format
    :return: Documents with specified {key: value} pair.
    """
    query_set = SchemaLoader.get_queryset(collection) if isinstance(
        collection, SchemaLoader) else None
    if not query_set:  # invalid model error log
        logger.error("Invalid model")
    if not isinstance(key, str):  # check to make sure key is a str
        logger.error("Invalid key")

    try:
        # get docs with {key: value} pair in collection
        docs = query_set.raw({key: value})
        # return doc as a json if desired
        return list(map(lambda d: d.as_json() if as_json else d, docs))
    except Exception as e:
        logger.error(repr(e))
        return None


def find_by_multi_key_value(collection: Enum, filter_map: dict, as_json: bool = False) -> str or dict:
    """
    Filter collection by {key: value} pair
    :param filter_map: The filter dictionary used to search in a collection
    :param collection: Name of collection for query
    :param as_json: Flag to signify if collection should be returned in JSON format
    :return: Documents with specified {key: value} pair.
    """
    query_set = SchemaLoader.get_queryset(collection) if isinstance(
        collection, SchemaLoader) else None
    if not query_set:  # invalid model error log
        logger.error("Invalid model")
    if not isinstance(filter_map, dict):  # check to make sure key is a str
        logger.error("Invalid filter")

    try:
        # get docs with {key: value} pair in collection
        docs = query_set.get(filter_map)
        return docs.as_json() if as_json else docs  # return doc as a json if desired
    except Exception as e:
        logger.error(repr(e))
        return None


def update_by_id(collection: Enum, obj_id: ObjectId, key: str, value):
    """
    Find the document specified by ID in the collection.
    Update it's field key to value.
    :param obj_id: The ID of the document to find
    :param collection: The collection to insert data in
    :param key: The key to update in the document
    :param value: The value to update key with
    :return: None
    """
    query_set = SchemaLoader.get_queryset(collection) if isinstance(
        collection, SchemaLoader) else None
    if not query_set:  # invalid model error log
        logger.error("Invalid model")
    if not isinstance(obj_id, ObjectId):
        logger.error("Invalid ID")
    if not isinstance(key, str):
        logger.error("Invalid key")

    try:
        # will make more sense to the user to have both jobs updated at the same time
        curr_datetime = datetime.utcnow()
        # desired fields to update
        update_input = {key: value, "updated_datetime": curr_datetime}
        query_set.raw({"_id": obj_id}).update({"$set": update_input})
        return True

    except Exception as e:
        logger.error(repr(e))
        return False


def insert_one(collection: Enum, data: dict) -> ObjectId:
    """
    Insert a Python dictionary into a collection.
    Update time to reflect when the collection was last altered
    :param data: The data to insert in collection
    :param collection: The collection to insert data in
    :return: ObjectId of doc added
    """
    model = SchemaLoader.get_model(collection) if isinstance(
        collection, SchemaLoader) else None
    if not model:  # invalid model error log
        logger.error("Invalid model")
    if not isinstance(data, dict):
        logger.error("Invalid data input") 

    try:
        new_doc = model.from_document(data)
        new_doc.created_datetime = datetime.utcnow()
        new_doc.started_datetime = None
        new_doc.updated_datetime = datetime.utcnow()
        new_doc.completed_datetime = None
        new_doc.save()
        return new_doc._id 
    except Exception as e:
        logger.error(repr(e))
        return None


def insert_many(collection: Enum, data: list) -> list:
    """
    Insert a list of Python dictionaries into a collection.
    Update time to reflect when the collection was last altered
    :param data: The list of data to insert in collection
    :param collection: The collection to insert data in
    :return: list of ObjectIds added
    """
    model = SchemaLoader.get_model(collection) if isinstance(
        collection, SchemaLoader) else None
    if not model:  # invalid model error log
        logger.error("Invalid model")
    if not isinstance(data, dict):
        logger.error("Invalid data input")

    try:
        obj_id_list = [] 
        for doc in data:
            new_doc = model.from_document(doc)
            new_doc.created_datetime = datetime.utcnow()
            new_doc.started_datetime = None
            new_doc.updated_datetime = datetime.utcnow()
            new_doc.completed_datetime = None
            new_doc.save()
            obj_id_list.append(new_doc._id)
        return obj_id_list
    except Exception as e:
        logger.error(repr(e))
        return None


def delete_by_id(collection: Enum, obj_id: ObjectId):
    """
    Delete document in collection that has specified id.
    Only works for single key filtering.
    :param obj_id: The id of the document to delete
    :param collection: Name of collection of interest
    :return: None
    """
    query_set = SchemaLoader.get_queryset(collection) if isinstance(
        collection, SchemaLoader) else None
    if not query_set:  # invalid model error log
        logger.error("Invalid model")
    if not isinstance(obj_id, ObjectId):  # check to make sure id is an ObjectId
        logger.error("Invalid ID")

    try:
        # remove docs with {key: value} pair in collection
        query_set.raw({"_id": obj_id}).delete()
    except Exception as e:
        logger.error(repr(e))
        return None


def delete_by_key_value(collection: Enum, key: str, value: str):
    """
    Delete document in collection that has {key: value} pair.
    Only works for single key filtering.
    :param key: The key to search for in a collection
    :param value: The desired value of key to delete in collection
    :param collection: Name of collection of interest
    :return: None
    """
    query_set = SchemaLoader.get_queryset(collection) if isinstance(
        collection, SchemaLoader) else None
    if not query_set:  # invalid model error log
        logger.error("Invalid model")
    if not isinstance(key, str):  # check to make sure key is a str
        logger.error("Invalid key")
    if not isinstance(value, str):  # check to make sure value is a str
        logger.error("Invalid value")

    try:
        # remove docs with {key: value} pair in collection
        query_set.raw({key: value}).delete()
    except Exception as e:
        logger.error(repr(e))
        return None
