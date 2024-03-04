"""
API server for querying the local MongoDB and posting
data to it.
To be used by the front end.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient

from model import Model, GTModel, WorkflowModel

import gt
import workflows
import releases
import runs

origins = [
    '*'
]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=['*'],
    allow_headers=['*'],
)

USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')

CLIENT = MongoClient(f'mongodb://{USERNAME}:{PASSWORD}@localhost:27017/results?authSource=results')
DB = CLIENT.results
COLL = DB.quiver


@app.get('/api/gt')
def api_get_all_gt() -> list:
    """
    Returns information about all available Ground Truth 
    curated by OCR-D for QuiVer
    """
    return gt.get_all_gt(COLL)


@app.get('/api/gt/{gt_id}')
def api_get_gt(gt_id: str) -> list:
    """
    Returns information about one available Ground Truth 
    curated by OCR-D for QuiVer
    """
    return gt.get_gt(COLL, gt_id)


@app.post('/api/gt')
def api_post_new_gt(gt_model: GTModel) -> str:
    """
    Posts information about a new Ground Truth dataset to the database.

    Args:
        - gt_model (GTModel): information about the GT
    Return
        - str: True if POST was successful
    """
    return gt.post_new_gt(COLL, gt_model)


@app.get('/api/workflows')
def get_all_workflows() -> list:
    """
    Returns information about all available workflows 
    curated by OCR-D for QuiVer
    """
    return workflows.get_all_workflows(COLL)


@app.get('/api/workflows/{wf_id}')
def get_workflows(wf_id: str) -> list:
    """
    Returns information about one available workflow
    curated by OCR-D for QuiVer
    """
    return workflows.get_workflows(COLL, wf_id)


@app.post('/api/workflows')
def post_new_workflow(workflow: WorkflowModel) -> str:
    """
    Posts information about a new workflow to the database.

    Args:
        - workflow (WorkflowModel): information about the workflow
    Return
        - bool: True if POST was successful
    """
    return workflows.post_new_workflow(COLL, workflow)

@app.get('/api/runs')
def get_all_runs() -> list:
    """
    Returns all evalutation results for all Quiver workspaces.
    """
    return runs.get_all_runs(COLL)


@app.get('/api/runs/latest')
def get_all_latest_runs() -> list:
    """
    Returns all evalutation results for all Quiver workspaces.
    """
    return runs.get_all_latest_runs(COLL)


@app.get('/api/runs/{gt_id}')
def get_all_runs_by_gt(gt_id: str,
                       start_date: str | None = None,
                       end_date: str | None = None) -> list:
    """
    Returns evalutation results for all Quiver workspaces with a 
    given GT

    Args:
        - gt_id (id): The ID of the GT data used for a run 
    """
    return runs.get_all_runs_by_gt(COLL, gt_id, start_date, end_date)


@app.get('/api/runs/{gt_id}/latest')
def get_latest_runs_per_gt(gt_id: str) -> list:
    """
    Returns evalutation results for the latest Quiver workspace with a 
    given GT

    Args:
        - gt_id (id): The ID of the GT data used for a run 
    """
    return runs.get_latest_runs_per_gt(COLL, gt_id)


@app.get('/api/runs/{gt_id}/{workflow_id}')
def get_all_runs_by_gt_and_wf(workflow_id: str,
                              gt_id: str,
                              start_date: str | None = None,
                              end_date: str | None = None) -> list:
    """
    Returns evalutation results for all Quiver workspaces with a 
    given workflow and GT

    Args:
        - workflow_id (str): The ID of the workflow used for a run
        - gt_id (id): The ID of the GT data used for a run 
    """
    return runs.get_all_runs_by_gt_and_wf(COLL, workflow_id, gt_id, start_date, end_date)


@app.get('/api/runs/{gt_id}/{workflow_id}/latest')
def get_latest_runs(workflow_id: str,
                    gt_id: str) -> list:
    """
    Returns evalutation results for the latest Quiver workspace with a 
    given workflow and GT

    Args:
        - workflow_id (str): The ID of the workflow used for a run
        - gt_id (id): The ID of the GT data used for a run 
    """
    return runs.get_latest_runs(COLL, workflow_id, gt_id)


@app.post("/api/runs")
def post_new_result(data: Model):
    """
    Posts information about a new evaluation workspace to the database.

    Args:
        - data (Model): information about the evaluation workspace
    Return
        - bool: True if POST was successful
    """
    return runs.post_new_result(COLL, data)

@app.get("/api/releases")
def get_releases():
    """
    Returns a list of all releases for which Quiver provides data.
    """
    return releases.get_all_releases(COLL)
