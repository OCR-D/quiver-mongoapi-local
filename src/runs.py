"""
This module handles all operations that deal with runs.
"""

import json
from datetime import datetime
from re import compile, Pattern
from bson import json_util
from pymongo import collection
from model import Model
from commons import remove_mongodb_id_from_result

from gt import get_all_gt
from workflows import get_all_workflows

def get_all_runs(coll: collection.Collection):
    """
    Returns all runs available in the DB, regardless of
    GT and workflow.
    """
    cursor = coll.find({'eval_workflow_id': {'$exists': True}})
    json_data = json.loads(json_util.dumps(cursor))

    return remove_mongodb_id_from_result(json_data, 'run')

def get_all_latest_runs(coll: collection.Collection):
    """
    Returns latest runs available in the DB, regardless of
    GT and workflow.
    """
    # get all gts
    all_gts = get_all_gt(coll)
    all_gt_ids = extract_ids(all_gts)
    # get all workflows
    all_workflows = get_all_workflows(coll)
    all_workflow_ids = extract_ids(all_workflows)
    # for each gt and each workflow, find the respective latest run
    latest_runs = []
    for gt in all_gt_ids:
        for wf in all_workflow_ids:
            latest_runs.append(get_latest_runs(coll, wf, gt))
    return latest_runs


def extract_ids(objects: list) -> list:
    """
    Returns the values of the resp. id properties of a list
    of JSON objects.
    """
    result = []
    for obj in objects:
        result.append(obj['id'])

    return result

def get_all_runs_by_gt(coll: collection.Collection,
                       gt_id: str,
                       start_date: str | None = None,
                       end_date: str | None = None) -> list:
    """
    Returns evalutation results for all Quiver workspaces with a 
    given GT

    Args:
        - gt_id (id): The ID of the GT data used for a run 
    """
    gt_regex = compile(gt_id)
    if start_date and end_date:
        json_data = find_results_within_date_range(coll, gt_regex, start_date, end_date)
    else:
        cursor = coll.find({'metadata.gt_workspace.id': gt_regex})
        json_data = json.loads(json_util.dumps(cursor))

    return remove_mongodb_id_from_result(json_data, 'run')


def get_all_runs_by_gt_and_wf(coll: collection.Collection,
                              workflow_id: str,
                              gt_id: str,
                              start_date: str | None = None,
                              end_date: str | None = None) -> list:
    """
    Returns evalutation results for all Quiver workspaces with a 
    given workflow and GT

    Args:
        - workflow_id (str): The ID of the workflow used for a run
        - gt_id (str): The ID of the GT data used for a run 
    """
    gt_regex = compile(gt_id)
    wf_regex = compile(workflow_id)
    if start_date and end_date:
        json_data = find_results_within_date_range(coll, gt_regex, start_date, end_date, wf_regex)
    else:
        cursor = coll.find({'$and': [{'metadata.gt_workspace.id': gt_regex},
                                    {'metadata.ocr_workflow.id': wf_regex}]})
        json_data = json.loads(json_util.dumps(cursor))
    return remove_mongodb_id_from_result(json_data, 'run')


def get_latest_runs(coll: collection.Collection,
                    workflow_id: str,
                    gt_id: str) -> list:
    """
    Returns evalutation results for the latest Quiver workspace with a 
    given workflow and GT

    Args:
        - workflow_id (str): The ID of the workflow used for a run
        - gt_id (id): The ID of the GT data used for a run 
    """
    wf_regex = compile(workflow_id)
    gt_regex = compile(gt_id)
    all_runs = coll.find({'$and': [{'metadata.gt_workspace.id': gt_regex},
                                 {'metadata.ocr_workflow.id': wf_regex}]})
    runs_json = json.loads(json_util.dumps(all_runs))
    closest_timestamp = find_timestamp_closest_to_today(runs_json)
    latest_run = coll.find({'$and': [{'metadata.gt_workspace.id': gt_regex},
                                 {'metadata.ocr_workflow.id': wf_regex},
                                 {'metadata.timestamp': compile(closest_timestamp)}]})
    latest_run_json = json.loads(json_util.dumps(latest_run))
    return remove_mongodb_id_from_result(latest_run_json, 'run')


def get_latest_runs_per_gt(coll: collection.Collection,
                           gt_id: str) -> list:
    """
    Returns evalutation results for the latest Quiver workspace with a 
    given GT

    Args:
        - gt_id (id): The ID of the GT data used for a run 
    """
    gt_regex = compile(gt_id)
    all_runs = coll.find({'metadata.gt_workspace.id': gt_regex})
    runs_json = json.loads(json_util.dumps(all_runs))
    closest_timestamp = find_timestamp_closest_to_today(runs_json)
    latest_run = coll.find({'$and': [{'metadata.gt_workspace.id': gt_regex},
                                 {'metadata.timestamp': compile(closest_timestamp)}]})
    latest_run_json = json.loads(json_util.dumps(latest_run))
    return remove_mongodb_id_from_result(latest_run_json, 'run')


def post_new_result(coll: collection.Collection,
                    data: Model):
    """
    Posts information about a new evaluation workspace to the database.

    Args:
        - data (Model): information about the evaluation workspace
    Return
        - bool: True if POST was successful
    """
    result = coll.insert_one(data.model_dump())
    return str(result.acknowledged)


def find_timestamp_closest_to_today(run_json: list) -> str:
    """
    Finds the timestamp in MongoDB that is closest to today's date.
    """
    # get all the dates
    timestamps_dates = get_timestamps(run_json)
    # find out which is the latest one
    current_date = datetime.today()
    closest_date = min(timestamps_dates, key=lambda d: abs(d - current_date))
    return datetime.strftime(closest_date, '%Y-%m-%d')


def get_timestamps(run_json: list) -> list:
    """
    Returns a list with all timestamps for a list of MongoDB
    query results.
    """
    timestamps_dates = []
    for entry in run_json:
        stamp = entry['metadata']['timestamp'].split('T')[0]
        stamp_datetime = datetime.strptime(stamp, '%Y-%m-%d')
        timestamps_dates.append(stamp_datetime)
    return timestamps_dates

def find_dates_within_range(timestamps: list,
                            start_datetime: datetime,
                            end_datetime: datetime) -> list:
    """
    Returns a list of all timestamps that are within a given rande.
    Args:
        - timestamps (list): a list of timestamps of the queried runs
        - start_datetime (datetime): the lower bound of the range
        - end_datetime (datetime): the upper bound of the range
    """
    relevant_dates = []
    for stamp in timestamps:
        if start_datetime <= stamp <= end_datetime:
            relevant_dates.append(stamp)
    return relevant_dates

def get_results_within_date_range(json_data_tmp, relevant_dates: list) -> list:
    """
    Returns all runs that have a timestamp that is within a given range.
    """
    json_data = []
    for entry in json_data_tmp:
        stamp = entry['metadata']['timestamp'].split('T')[0]
        stamp_datetime = datetime.strptime(stamp, '%Y-%m-%d')
        if stamp_datetime in relevant_dates:
            json_data.append(entry)
    return json_data

def find_results_within_date_range(coll: collection.Collection,
                                   gt_regex: Pattern,
                                   start_date: str,
                                   end_date: str,
                                   wf_regex: Pattern | None = None) -> list:
    """
    Returns all runs that match a given GT, a given workspace (optional)
    and a given date filter.
    """
    start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
    end_datetime = datetime.strptime(end_date, '%Y-%m-%d')

    if wf_regex:
        cursor = coll.find({'$and': [{'metadata.gt_workspace.id': gt_regex},
                                    {'metadata.ocr_workflow.id': wf_regex}]})
    else:
        cursor = coll.find({'metadata.gt_workspace.id': gt_regex})
    json_data_tmp = json.loads(json_util.dumps(cursor))
    timestamps_dates = get_timestamps(json_data_tmp)

    relevant_dates = find_dates_within_range(timestamps_dates, start_datetime, end_datetime)

    return get_results_within_date_range(json_data_tmp, relevant_dates)
