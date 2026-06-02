"""设备管理服务"""
from typing import Optional

from app.models.equipment import EquipmentDetail, EquipmentListResponse, EquipmentStatsResponse
from app.mock_data.equipment import (
    get_equipment_by_id,
    get_equipment_list,
    get_equipment_stats,
)


class EquipmentService:
    """设备管理服务"""

    async def list_equipment(
        self,
        page: int = 1,
        page_size: int = 10,
        equipment_type: Optional[str] = None,
        status: Optional[str] = None,
        substation: Optional[str] = None,
        keyword: Optional[str] = None,
    ) -> EquipmentListResponse:
        """获取设备列表"""
        result = get_equipment_list(
            page=page,
            page_size=page_size,
            equipment_type=equipment_type,
            status=status,
            substation=substation,
            keyword=keyword,
        )

        items = [EquipmentDetail(**eq) for eq in result["items"]]

        return EquipmentListResponse(
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"],
            items=items,
        )

    async def get_equipment(self, equipment_id: str) -> EquipmentDetail | None:
        """获取设备详情"""
        eq = get_equipment_by_id(equipment_id)
        if not eq:
            return None
        return EquipmentDetail(**eq)

    async def get_stats(self) -> EquipmentStatsResponse:
        """获取设备统计概览"""
        stats = get_equipment_stats()
        return EquipmentStatsResponse(**stats)
