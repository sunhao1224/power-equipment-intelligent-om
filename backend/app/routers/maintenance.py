"""维护决策路由"""
from fastapi import APIRouter, Depends

from app.models.common import ApiResponse
from app.models.maintenance import (
    MaintenancePlanRequest,
    MaintenancePlanResponse,
)
from app.services.maintenance_service import MaintenanceService

router = APIRouter()

_maintenance_service = MaintenanceService()


def get_maintenance_service() -> MaintenanceService:
    return _maintenance_service


@router.post("/plan", response_model=ApiResponse[MaintenancePlanResponse])
async def generate_plan(
    request: MaintenancePlanRequest,
    service: MaintenanceService = Depends(get_maintenance_service),
):
    """生成维护计划"""
    result = await service.generate_plan(request)
    return ApiResponse(data=result)
