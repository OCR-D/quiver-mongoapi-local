"""
This module handles all operations that deal with Ground Truth Data.
"""

import json
from bson import json_util
from re import compile
from pymongo import collection
from model import GTModel
from commons import remove_mongodb_id_from_result

def get_all_gt(coll: collection.Collection) -> list:
    """
    Returns information about all available Ground Truth 
    curated by OCR-D for QuiVer
    """
    cursor = coll.find({'gt_workspace': {'$exists': True}})
    json_data = json.loads(json_util.dumps(cursor))

    return remove_mongodb_id_from_result(json_data, 'gt')


def get_gt(coll: collection.Collection, gt_id: str) -> list:
    """
    Returns information about one available Ground Truth 
    curated by OCR-D for QuiVer
    """
    gt_regex = compile(gt_id)
    cursor = coll.find({'gt_workspace.id': gt_regex})
    json_data = json.loads(json_util.dumps(cursor))

    return remove_mongodb_id_from_result(json_data, 'gt')


def post_new_gt(coll: collection.Collection, gt: GTModel) -> str:
    """
    Posts information about a new Ground Truth dataset to the database.

    Args:
        - gt (GTModel): information about the GT
    Return
        - bool: True if POST was successful
    """
    result = coll.insert_one(gt.model_dump())
    return str(result.acknowledged)
