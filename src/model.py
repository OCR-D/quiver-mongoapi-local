from __future__ import annotations

from typing import Any, List

from pydantic import BaseModel, Field


class OcrWorkflow(BaseModel):
    id: str = Field(..., alias='@id')
    label: str


class EvalWorkflow(BaseModel):
    id: str = Field(..., alias='@id')
    label: str


class GtWorkspace(BaseModel):
    id: str = Field(..., alias='@id')
    label: str
    metadata: dict

class GtWorkspaceRuns(BaseModel):
    id: str = Field(..., alias='@id')
    label: str

class OcrWorkspace(BaseModel):
    id: str = Field(..., alias='@id')
    label: str


class EvalWorkspace(BaseModel):
    id: str = Field(..., alias='@id')
    label: str


class WorkflowStep(BaseModel):
    id: str
    params: Any


class DataProperties(BaseModel):
    fonts: List[str]
    publication_century: str
    publication_decade: str
    publication_year: str
    number_of_pages: int
    layout: str


class DocumentMetadata(BaseModel):
    data_properties: DataProperties


class Metadata(BaseModel):
    ocr_workflow: OcrWorkflow
    eval_workflow: EvalWorkflow
    gt_workspace: GtWorkspaceRuns
    ocr_workspace: OcrWorkspace
    eval_workspace: EvalWorkspace
    workflow_steps: List[WorkflowStep]
    workflow_model: str
    eval_tool: str
    document_metadata: DocumentMetadata
    timestamp: str
    release_info: Release

class Author(BaseModel):
    login: str
    id: int
    node_id: str
    avatar_url: str
    gravatar_id: str
    url: str
    html_url: str
    followers_url: str
    following_url: str
    gists_url: str
    starred_url: str
    subscriptions_url: str
    organizations_url: str
    repos_url: str
    events_url: str
    received_events_url: str
    type: str
    site_admin: bool


class Release(BaseModel):
    url: str
    assets_url: str
    upload_url: str
    html_url: str
    id: int
    author: Author
    node_id: str
    tag_name: str
    target_commitish: str
    name: str
    draft: bool
    prerelease: bool
    created_at: str
    published_at: str
    assets: List
    tarball_url: str
    zipball_url: str
    body: str
    mentions_count: int | None = None

class DocumentWide(BaseModel):
    wall_time: float
    cpu_time: float | None = None
    cer_mean: float
    cer_median: float
    cer_range: List[float]
    cer_standard_deviation: Any
    wer: float
    pages_per_minute: float


class ByPageItem(BaseModel):
    page_id: str
    cer: float
    wer: float


class EvaluationResults(BaseModel):
    document_wide: DocumentWide
    by_page: List[ByPageItem]


class Model(BaseModel):
    eval_workflow_id: str
    label: str
    metadata: Metadata
    evaluation_results: EvaluationResults

class GTModel(BaseModel):
    gt_workspace: GtWorkspace

class WorkflowModel(BaseModel):
    id: str = Field(..., alias='@id')
    label: str
    steps: List[WorkflowStep]
    model: str
