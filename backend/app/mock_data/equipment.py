"""设备台账 Mock 数据"""
from datetime import date
from typing import Optional

# 设备类型枚举
EQUIPMENT_TYPES = {
    "transformer": "变压器",
    "breaker": "断路器",
    "gis": "GIS组合电器",
}

# 设备状态
STATUS_MAP = {
    "normal": "正常",
    "warning": "告警",
    "fault": "故障",
    "maintenance": "检修中",
}

# 设备台账数据
EQUIPMENT_LIST: list[dict] = [
    {
        "equipment_id": "TR-001",
        "name": "1号主变",
        "type": "transformer",
        "type_name": "变压器",
        "model": "SFZ11-120000/220",
        "manufacturer": "特变电工",
        "voltage_level": "220kV",
        "capacity": "120MVA",
        "substation": "滨江变电站",
        "substation_id": "SUB-001",
        "commission_date": "2015-06-15",
        "status": "normal",
        "status_name": "正常",
        "health_index": 92.5,
        "location": "浙江省杭州市滨江区",
        "longitude": 120.21,
        "latitude": 30.21,
        "last_maintenance_date": "2024-08-20",
        "next_maintenance_date": "2025-08-20",
        "operating_hours": 72360,
        "rated_current": 314.0,
        "impedance_voltage": 12.5,
        "oil_weight": 35.0,
        "total_weight": 125.0,
    },
    {
        "equipment_id": "TR-002",
        "name": "2号主变",
        "type": "transformer",
        "type_name": "变压器",
        "model": "SFZ11-120000/220",
        "manufacturer": "特变电工",
        "voltage_level": "220kV",
        "capacity": "120MVA",
        "substation": "滨江变电站",
        "substation_id": "SUB-001",
        "commission_date": "2015-06-15",
        "status": "warning",
        "status_name": "告警",
        "health_index": 78.3,
        "location": "浙江省杭州市滨江区",
        "longitude": 120.21,
        "latitude": 30.21,
        "last_maintenance_date": "2024-03-10",
        "next_maintenance_date": "2025-03-10",
        "operating_hours": 72360,
        "rated_current": 314.0,
        "impedance_voltage": 12.5,
        "oil_weight": 35.0,
        "total_weight": 125.0,
    },
    {
        "equipment_id": "TR-003",
        "name": "1号主变",
        "type": "transformer",
        "type_name": "变压器",
        "model": "SSZ11-150000/220",
        "manufacturer": "西电集团",
        "voltage_level": "220kV",
        "capacity": "150MVA",
        "substation": "西湖变电站",
        "substation_id": "SUB-002",
        "commission_date": "2018-09-20",
        "status": "normal",
        "status_name": "正常",
        "health_index": 95.2,
        "location": "浙江省杭州市西湖区",
        "longitude": 120.15,
        "latitude": 30.27,
        "last_maintenance_date": "2024-11-05",
        "next_maintenance_date": "2025-11-05",
        "operating_hours": 54000,
        "rated_current": 393.0,
        "impedance_voltage": 14.0,
        "oil_weight": 42.0,
        "total_weight": 155.0,
    },
    {
        "equipment_id": "TR-004",
        "name": "3号主变",
        "type": "transformer",
        "type_name": "变压器",
        "model": "SFZ10-90000/110",
        "manufacturer": "保定天威",
        "voltage_level": "110kV",
        "capacity": "90MVA",
        "substation": "余杭变电站",
        "substation_id": "SUB-003",
        "commission_date": "2012-03-10",
        "status": "warning",
        "status_name": "告警",
        "health_index": 68.7,
        "location": "浙江省杭州市余杭区",
        "longitude": 120.30,
        "latitude": 30.42,
        "last_maintenance_date": "2024-05-15",
        "next_maintenance_date": "2025-05-15",
        "operating_hours": 95040,
        "rated_current": 472.0,
        "impedance_voltage": 10.5,
        "oil_weight": 22.0,
        "total_weight": 85.0,
    },
    {
        "equipment_id": "CB-001",
        "name": "220kV滨西线断路器",
        "type": "breaker",
        "type_name": "断路器",
        "model": "LW36-252/T4000-50",
        "manufacturer": "平高电气",
        "voltage_level": "220kV",
        "capacity": "4000A",
        "substation": "滨江变电站",
        "substation_id": "SUB-001",
        "commission_date": "2015-06-15",
        "status": "normal",
        "status_name": "正常",
        "health_index": 88.9,
        "location": "浙江省杭州市滨江区",
        "longitude": 120.21,
        "latitude": 30.21,
        "last_maintenance_date": "2024-09-12",
        "next_maintenance_date": "2025-09-12",
        "operating_hours": 72360,
        "breaking_capacity": "50kA",
        "sf6_pressure": 0.58,
        "operation_count": 1256,
    },
    {
        "equipment_id": "CB-002",
        "name": "220kV滨东线断路器",
        "type": "breaker",
        "type_name": "断路器",
        "model": "LW36-252/T4000-50",
        "manufacturer": "平高电气",
        "voltage_level": "220kV",
        "capacity": "4000A",
        "substation": "滨江变电站",
        "substation_id": "SUB-001",
        "commission_date": "2015-06-15",
        "status": "normal",
        "status_name": "正常",
        "health_index": 91.2,
        "location": "浙江省杭州市滨江区",
        "longitude": 120.21,
        "latitude": 30.21,
        "last_maintenance_date": "2024-10-08",
        "next_maintenance_date": "2025-10-08",
        "operating_hours": 72360,
        "breaking_capacity": "50kA",
        "sf6_pressure": 0.60,
        "operation_count": 982,
    },
    {
        "equipment_id": "CB-003",
        "name": "110kV余北线断路器",
        "type": "breaker",
        "type_name": "断路器",
        "model": "LW30-126/T3150-40",
        "manufacturer": "河南森源",
        "voltage_level": "110kV",
        "capacity": "3150A",
        "substation": "余杭变电站",
        "substation_id": "SUB-003",
        "commission_date": "2012-03-10",
        "status": "fault",
        "status_name": "故障",
        "health_index": 45.2,
        "location": "浙江省杭州市余杭区",
        "longitude": 120.30,
        "latitude": 30.42,
        "last_maintenance_date": "2024-01-20",
        "next_maintenance_date": "2025-01-20",
        "operating_hours": 95040,
        "breaking_capacity": "40kA",
        "sf6_pressure": 0.52,
        "operation_count": 2341,
    },
    {
        "equipment_id": "GIS-001",
        "name": "220kV GIS",
        "type": "gis",
        "type_name": "GIS组合电器",
        "model": "ZF-252/T4000-50",
        "manufacturer": "西开电气",
        "voltage_level": "220kV",
        "capacity": "4000A",
        "substation": "西湖变电站",
        "substation_id": "SUB-002",
        "commission_date": "2018-09-20",
        "status": "normal",
        "status_name": "正常",
        "health_index": 96.1,
        "location": "浙江省杭州市西湖区",
        "longitude": 120.15,
        "latitude": 30.27,
        "last_maintenance_date": "2024-12-01",
        "next_maintenance_date": "2025-12-01",
        "operating_hours": 54000,
        "bay_count": 8,
        "sf6_pressure": 0.55,
        "compartment_count": 24,
    },
    {
        "equipment_id": "GIS-002",
        "name": "110kV GIS",
        "type": "gis",
        "type_name": "GIS组合电器",
        "model": "ZF-126/T3150-40",
        "manufacturer": "正泰电气",
        "voltage_level": "110kV",
        "capacity": "3150A",
        "substation": "余杭变电站",
        "substation_id": "SUB-003",
        "commission_date": "2016-11-08",
        "status": "normal",
        "status_name": "正常",
        "health_index": 89.5,
        "location": "浙江省杭州市余杭区",
        "longitude": 120.30,
        "latitude": 30.42,
        "last_maintenance_date": "2024-07-18",
        "next_maintenance_date": "2025-07-18",
        "operating_hours": 69120,
        "bay_count": 6,
        "sf6_pressure": 0.53,
        "compartment_count": 18,
    },
    {
        "equipment_id": "TR-005",
        "name": "2号主变",
        "type": "transformer",
        "type_name": "变压器",
        "model": "SFZ11-180000/500",
        "manufacturer": "西电集团",
        "voltage_level": "500kV",
        "capacity": "180MVA",
        "substation": "萧山变电站",
        "substation_id": "SUB-004",
        "commission_date": "2020-05-25",
        "status": "normal",
        "status_name": "正常",
        "health_index": 97.8,
        "location": "浙江省杭州市萧山区",
        "longitude": 120.27,
        "latitude": 30.18,
        "last_maintenance_date": "2025-01-10",
        "next_maintenance_date": "2026-01-10",
        "operating_hours": 43200,
        "rated_current": 208.0,
        "impedance_voltage": 16.0,
        "oil_weight": 55.0,
        "total_weight": 210.0,
    },
    {
        "equipment_id": "CB-004",
        "name": "500kV萧浦线断路器",
        "type": "breaker",
        "type_name": "断路器",
        "model": "HPL-550/T4000-63",
        "manufacturer": "ABB",
        "voltage_level": "500kV",
        "capacity": "4000A",
        "substation": "萧山变电站",
        "substation_id": "SUB-004",
        "commission_date": "2020-05-25",
        "status": "normal",
        "status_name": "正常",
        "health_index": 94.6,
        "location": "浙江省杭州市萧山区",
        "longitude": 120.27,
        "latitude": 30.18,
        "last_maintenance_date": "2025-01-10",
        "next_maintenance_date": "2026-01-10",
        "operating_hours": 43200,
        "breaking_capacity": "63kA",
        "sf6_pressure": 0.62,
        "operation_count": 456,
    },
    {
        "equipment_id": "GIS-003",
        "name": "500kV GIS",
        "type": "gis",
        "type_name": "GIS组合电器",
        "model": "ELK-3-550",
        "manufacturer": "ABB",
        "voltage_level": "500kV",
        "capacity": "4000A",
        "substation": "萧山变电站",
        "substation_id": "SUB-004",
        "commission_date": "2020-05-25",
        "status": "maintenance",
        "status_name": "检修中",
        "health_index": 85.3,
        "location": "浙江省杭州市萧山区",
        "longitude": 120.27,
        "latitude": 30.18,
        "last_maintenance_date": "2025-02-01",
        "next_maintenance_date": "2026-02-01",
        "operating_hours": 43200,
        "bay_count": 10,
        "sf6_pressure": 0.58,
        "compartment_count": 30,
    },
]


def get_equipment_by_id(equipment_id: str) -> Optional[dict]:
    """根据ID获取设备"""
    for eq in EQUIPMENT_LIST:
        if eq["equipment_id"] == equipment_id:
            return eq
    return None


def get_equipment_list(
    page: int = 1,
    page_size: int = 10,
    equipment_type: Optional[str] = None,
    status: Optional[str] = None,
    substation: Optional[str] = None,
    keyword: Optional[str] = None,
) -> dict:
    """获取设备列表（分页+筛选）"""
    filtered = EQUIPMENT_LIST

    if equipment_type:
        filtered = [e for e in filtered if e["type"] == equipment_type]
    if status:
        filtered = [e for e in filtered if e["status"] == status]
    if substation:
        filtered = [e for e in filtered if e["substation"] == substation]
    if keyword:
        filtered = [
            e for e in filtered
            if keyword.lower() in e["name"].lower()
            or keyword.lower() in e["equipment_id"].lower()
            or keyword.lower() in e["model"].lower()
        ]

    total = len(filtered)
    start = (page - 1) * page_size
    end = start + page_size
    items = filtered[start:end]

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items,
    }


def get_equipment_stats() -> dict:
    """设备统计概览"""
    total = len(EQUIPMENT_LIST)
    by_type = {}
    by_status = {}
    by_substation = {}
    health_scores = []

    for eq in EQUIPMENT_LIST:
        # 按类型统计
        t = eq["type_name"]
        by_type[t] = by_type.get(t, 0) + 1

        # 按状态统计
        s = eq["status_name"]
        by_status[s] = by_status.get(s, 0) + 1

        # 按变电站统计
        sub = eq["substation"]
        if sub not in by_substation:
            by_substation[sub] = {"total": 0, "normal": 0, "warning": 0, "fault": 0}
        by_substation[sub]["total"] += 1
        if eq["status"] == "normal":
            by_substation[sub]["normal"] += 1
        elif eq["status"] == "warning":
            by_substation[sub]["warning"] += 1
        elif eq["status"] in ("fault", "maintenance"):
            by_substation[sub]["fault"] += 1

        health_scores.append(eq["health_index"])

    avg_health = round(sum(health_scores) / len(health_scores), 1) if health_scores else 0

    return {
        "total": total,
        "by_type": by_type,
        "by_status": by_status,
        "by_substation": by_substation,
        "avg_health_index": avg_health,
        "warning_count": by_status.get("告警", 0),
        "fault_count": by_status.get("故障", 0),
    }
