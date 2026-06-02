"""设备管理路由"""
from typing import Optional
from fastapi import APIRouter, Depends

from app.models.common import ApiResponse
from app.models.equipment import EquipmentDetail, EquipmentListResponse, EquipmentStatsResponse
from app.models.maintenance import HealthResponse
from app.services.equipment_service import EquipmentService
from app.services.maintenance_service import MaintenanceService

router = APIRouter()

_equipment_service = EquipmentService()
_maintenance_service = MaintenanceService()


def get_equipment_service() -> EquipmentService:
    return _equipment_service


def get_maintenance_service() -> MaintenanceService:
    return _maintenance_service


@router.get("", response_model=ApiResponse[EquipmentListResponse])
async def list_equipment(
    page: int = 1,
    page_size: int = 10,
    equipment_type: Optional[str] = None,
    status: Optional[str] = None,
    substation: Optional[str] = None,
    keyword: Optional[str] = None,
    service: EquipmentService = Depends(get_equipment_service),
):
    """获取设备列表（支持分页、筛选）"""
    result = await service.list_equipment(
        page=page,
        page_size=page_size,
        equipment_type=equipment_type,
        status=status,
        substation=substation,
        keyword=keyword,
    )
    return ApiResponse(data=result)


@router.get("/stats", response_model=ApiResponse[EquipmentStatsResponse])
async def equipment_stats(
    service: EquipmentService = Depends(get_equipment_service),
):
    """设备统计概览（Dashboard用）"""
    result = await service.get_stats()
    return ApiResponse(data=result)


@router.get("/{equipment_id}/health", response_model=ApiResponse[HealthResponse | None])
async def get_equipment_health(
    equipment_id: str,
    service: MaintenanceService = Depends(get_maintenance_service),
):
    """获取设备健康评分"""
    result = await service.get_health(equipment_id)
    if result is None:
        return ApiResponse(code=404, message=f"设备 {equipment_id} 不存在", data=None)
    return ApiResponse(data=result)


@router.get("/{equipment_id}", response_model=ApiResponse[EquipmentDetail | None])
async def get_equipment(
    equipment_id: str,
    service: EquipmentService = Depends(get_equipment_service),
):
    """获取设备详情"""
    result = await service.get_equipment(equipment_id)
    if result is None:
        return ApiResponse(code=404, message=f"设备 {equipment_id} 不存在", data=None)
    return ApiResponse(data=result)
