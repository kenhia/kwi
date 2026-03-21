"""Data models for kwi entities."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Project:
    id: int
    project: str
    cn_path: str
    gh_repo: str | None = None
    description: str | None = None
    created: datetime | None = None
    updated: datetime | None = None


@dataclass
class Area:
    id: int
    project_id: int
    name: str
    description: str | None = None


@dataclass
class WorkItem:
    id: int
    project_id: int
    title: str
    content: str
    wi_type: str
    wi_status: str
    wi_tshirt: str = "Unknown"
    area_id: int | None = None
    area_name: str | None = None
    project_name: str | None = None
    sprint: str | None = None
    details: str | None = None
    parent_id: int | None = None
    created: datetime | None = None
    updated: datetime | None = None


@dataclass
class Related:
    id: int
    left_id: int
    right_id: int
    relationship: str
