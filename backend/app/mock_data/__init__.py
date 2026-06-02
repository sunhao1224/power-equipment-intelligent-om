"""Mock 数据模块"""
from app.mock_data.equipment import EQUIPMENT_LIST, get_equipment_by_id
from app.mock_data.sensors import get_sensor_data, get_dga_data
from app.mock_data.faults import FAULT_CASES
from app.mock_data.knowledge import KNOWLEDGE_BASE
from app.mock_data.health import get_health_data

__all__ = [
    "EQUIPMENT_LIST",
    "get_equipment_by_id",
    "get_sensor_data",
    "get_dga_data",
    "FAULT_CASES",
    "KNOWLEDGE_BASE",
    "get_health_data",
]
