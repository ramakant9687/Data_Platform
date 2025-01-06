from enum import Enum
from typing import Any

from pydantic import BaseModel


class JobCreateRequest(BaseModel):
    name: str
    adp_job_id: str
    adp_project_id: str
    biz_crit_score: int
    env: str
    dri: int
    team: int
    lob: int
    service_account: int


class Job(BaseModel):
    id: int
    name: str
    adp_job_id: str
    adp_project_id: str
    biz_crit_score: int
    env: str
    dri: int
    team: int
    lob: int
    service_account: int


class APIRequestMethod(str, Enum):
    get = "GET"
    post = "POST"
    patch = "PATCH"
    delete = "DELETE"


class APIRequest(BaseModel):
    url: str
    method: APIRequestMethod
    headers: dict[str, str] | None = None
    params: dict[str, Any] | None = None
    json_data: dict[str, Any] | None = None
