"""Pydantic models for initial YAML contracts."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class StepRef(BaseModel):
    id: str = Field(min_length=1)
    skill: str = Field(min_length=1)


class TriggerConfig(BaseModel):
    type: Literal["schedule", "event"] = "schedule"
    every_minutes: int = Field(default=10, ge=1, le=10080)


class AgentConfig(BaseModel):
    schema_version: str = "v1alpha1"
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    timezone: str = "UTC"
    trigger: TriggerConfig
    steps: list[StepRef] = Field(default_factory=list)
    created_at: datetime | None = None
