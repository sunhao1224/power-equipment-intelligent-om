"""Pydantic 模型"""
from app.models.common import ApiResponse
from app.models.chat import ChatRequest, ChatResponse, Reference
from app.models.diagnosis import (
    DiagnosisTriggerRequest,
    DiagnosisTriggerResponse,
    DiagnosisReport,
)
from app.models.batch import BatchAssessRequest, BatchAssessResponse
from app.models.maintenance import (
    MaintenancePlanRequest,
    MaintenancePlanResponse,
    HealthResponse,
)
from app.models.knowledge import KnowledgeUploadRequest, KnowledgeSearchRequest, KnowledgeSearchResponse
from app.models.equipment import EquipmentDetail, EquipmentListResponse, EquipmentStatsResponse

__all__ = [
    "ApiResponse",
    "ChatRequest", "ChatResponse", "Reference",
    "DiagnosisTriggerRequest", "DiagnosisTriggerResponse", "DiagnosisReport",
    "BatchAssessRequest", "BatchAssessResponse",
    "MaintenancePlanRequest", "MaintenancePlanResponse", "HealthResponse",
    "KnowledgeUploadRequest", "KnowledgeSearchRequest", "KnowledgeSearchResponse",
    "EquipmentDetail", "EquipmentListResponse", "EquipmentStatsResponse",
]
