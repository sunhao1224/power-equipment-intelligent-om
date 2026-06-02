"""设备管理模型"""
from typing import Optional
from pydantic import BaseModel, Field


class EquipmentDetail(BaseModel):
    """设备详情"""
    equipment_id: str
    name: str
    type: str
    type_name: str
    model: str
    manufacturer: str
    voltage_level: str
    capacity: str
    substation: str
    substation_id: str
    commission_date: str
    status: str
    status_name: str
    health_index: float
    location: str = ""
    longitude: float = 0
    latitude: float = 0
    last_maintenance_date: str = ""
    next_maintenance_date: str = ""
    operating_hours: int = 0


class EquipmentListResponse(BaseModel):
    """设备列表响应"""
    total: int
    page: int
    page_size: int
    items: list[EquipmentDetail]


class EquipmentStatsResponse(BaseModel):
    """设备统计概览"""
    total: int
    by_type: dict
    by_status: dict
    by_substation: dict
    avg_health_index: float
    warning_count: int
    fault_count: int
