"""Shared API contracts for the Hermes Agent service."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class ApiResponse(BaseModel):
    code: int = 0
    message: str = "ok"
    data: Any = None


class DiagnosisInput(BaseModel):
    equipment_id: str
    event_type: Literal["mock_event", "historical_replay", "manual_upload"]
    event_id: str | None = None
    sensor_data: dict[str, Any] = Field(default_factory=dict)
    time_window: str = "24h"
    priority: Literal["normal", "important", "urgent"] = "important"
    edge_context: dict[str, Any] | None = None


class BatchAssessmentRequest(BaseModel):
    equipment_id: str
    batch_criteria: dict[str, Any] = Field(default_factory=dict)


class EvidenceItem(BaseModel):
    evidence_id: str
    title: str
    source_type: Literal["regulation", "case", "graph", "timeseries", "standard"]
    source_id: str
    content: str
    confidence: float
    linked_nodes: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class AgentNode(BaseModel):
    agent_id: str
    name: str
    role: str
    status: Literal["pending", "spawned", "running", "tool_calling", "completed", "failed", "need_human_review"] = "pending"
    progress: int = 0
    confidence: float = 0.0
    evidence_count: int = 0
    duration_ms: int = 0
    summary: str = ""


class ToolCall(BaseModel):
    call_id: str
    agent_id: str
    tool_name: str
    request_summary: str
    response_summary: str
    latency_ms: int
    status: Literal["completed", "failed"] = "completed"


class SkillCall(BaseModel):
    call_id: str
    agent_id: str
    skill_name: str
    skill_version: str = "v1"
    status: Literal["completed", "failed"] = "completed"


class AgentTrace(BaseModel):
    trace_id: str
    diagnosis_id: str
    orchestrator_id: str
    status: Literal["pending", "running", "reviewing", "completed", "failed"] = "pending"
    started_at: datetime
    completed_at: datetime | None = None
    agent_steps: list[AgentNode] = Field(default_factory=list)
    tool_calls: list[ToolCall] = Field(default_factory=list)
    skill_calls: list[SkillCall] = Field(default_factory=list)
    evidence_links: list[EvidenceItem] = Field(default_factory=list)


class BatchRiskItem(BaseModel):
    equipment_id: str
    equipment_name: str
    manufacturer: str
    model: str
    batch_no: str
    location: str
    risk_level: Literal["low", "medium", "high", "critical"]
    probability_6m: float
    probability_12m: float
    probability_24m: float
    reason: str


class FmeaItem(BaseModel):
    failure_mode: str
    component: str
    severity: int
    occurrence: int
    detection: int
    rpn: int
    recommendation: str


class WorkOrderDraft(BaseModel):
    title: str
    priority: Literal["normal", "important", "urgent"]
    actions: list[str]
    required_roles: list[str]
    spare_parts: list[str]
    safety_notes: list[str]
    estimated_hours: float


class ReportSummary(BaseModel):
    report_id: str
    diagnosis_id: str
    equipment_id: str
    title: str
    risk_level: Literal["normal", "important", "urgent"]
    root_causes: list[dict[str, Any]]
    component_path: list[str]
    batch_risks: list[BatchRiskItem]
    fmea: list[FmeaItem]
    work_order: WorkOrderDraft
    review_findings: list[dict[str, Any]]
    evidence_ids: list[str]
    created_at: datetime


class DiagnosisTask(BaseModel):
    diagnosis_id: str
    orchestrator_id: str
    agent_trace_id: str
    status: Literal["pending", "running", "reviewing", "completed", "failed"]
    input: DiagnosisInput
    agents_output: list[AgentNode] = Field(default_factory=list)
    report: ReportSummary | None = None
    review_findings: list[dict[str, Any]] = Field(default_factory=list)


class WebSocketEvent(BaseModel):
    event_type: str
    diagnosis_id: str
    timestamp: datetime
    payload: dict[str, Any] = Field(default_factory=dict)
