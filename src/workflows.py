"""
This module handles all operations that deal with workflows.
"""

import json
from bson import json_util
from re import compile
from pymongo import collection
from model import WorkflowModel
from commons import remove_mongodb_id_from_result

def get_all_workflows(coll: collection.Collection) -> list:
    """
    Returns information about all available workflows 
    curated by OCR-D for QuiVer
    """
    cursor = coll.find({'steps': {'$exists': True}})
    json_data = json.loads(json_util.dumps(cursor))

    return remove_mongodb_id_from_result(json_data, 'workflows')

def get_workflows(coll: collection.Collection, wf_id: str) -> list:
    """
    Returns information about one available workflow
    curated by OCR-D for QuiVer
    """
    wf_regex = compile(wf_id)
    cursor = coll.find({'id': wf_regex})
    json_data = json.loads(json_util.dumps(cursor))

    return remove_mongodb_id_from_result(json_data, 'workflows')


def post_new_workflow(coll: collection.Collection, wf: WorkflowModel) -> str:
    """
    Posts information about a new workflow to the database.

    Args:
        - workflow (WorkflowModel): information about the workflow
    Return
        - bool: True if POST was successful
    """
    result = coll.insert_one(wf.model_dump())
    return str(result.acknowledged)
