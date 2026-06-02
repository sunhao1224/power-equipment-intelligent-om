"""维护决策服务"""
import uuid
from datetime import datetime, timedelta

from app.models.maintenance import (
    MaintenancePlanRequest,
    MaintenancePlanResponse,
    MaintenancePlanItem,
    WorkOrder,
    HealthResponse,
)
from app.mock_data.equipment import get_equipment_by_id
from app.mock_data.health import get_health_data


class MaintenanceService:
    """维护决策服务"""

    async def generate_plan(self, request: MaintenancePlanRequest) -> MaintenancePlanResponse:
        """生成维护计划"""
        plans = []
        work_orders = []
        now = datetime.now()

        for eq_id in request.equipment_ids:
            eq = get_equipment_by_id(eq_id)
            if not eq:
                continue

            health = get_health_data(eq_id)
            health_index = health["health_index"]

            # 根据健康指数确定计划类型和紧急程度
            if health_index >= 90:
                plan_type = "例行维护"
                urgency = "low"
                days_offset = request.time_horizon - 10
            elif health_index >= 70:
                plan_type = "状态检修"
                urgency = "normal"
                days_offset = min(30, request.time_horizon // 3)
            elif health_index >= 50:
                plan_type = "专项检修"
                urgency = "high"
                days_offset = min(14, request.time_horizon // 6)
            else:
                plan_type = "紧急检修"
                urgency = "critical"
                days_offset = min(3, request.time_horizon // 10)

            planned_date = (now + timedelta(days=days_offset)).strftime("%Y-%m-%d")

            # 建议措施
            recommended_actions = self._get_recommended_actions(eq, health_index, health)

            plans.append(MaintenancePlanItem(
                equipment_id=eq_id,
                equipment_name=eq["name"],
                health_index=health_index,
                plan_type=plan_type,
                recommended_actions=recommended_actions,
                planned_date=planned_date,
                urgency=urgency,
            ))

            # 生成工单
            priority_map = {"critical": 1, "high": 2, "normal": 3, "low": 4}
            hours_map = {"紧急检修": 48, "专项检修": 24, "状态检修": 16, "例行维护": 8}

            work_orders.append(WorkOrder(
                order_id=f"WO-{uuid.uuid4().hex[:8].upper()}",
                equipment_id=eq_id,
                equipment_name=eq["name"],
                task_type=plan_type,
                priority=priority_map.get(urgency, 3),
                planned_date=planned_date,
                estimated_hours=hours_map.get(plan_type, 8),
                description=f"{eq['name']}{plan_type}：健康指数{health_index}分，"
                            f"需进行{recommended_actions[0] if recommended_actions else '常规检查'}",
                status="planned",
            ))

        # 按紧急程度排序
        urgency_order = {"critical": 0, "high": 1, "normal": 2, "low": 3}
        plans.sort(key=lambda p: urgency_order.get(p.urgency, 3))
        work_orders.sort(key=lambda w: w.priority)

        return MaintenancePlanResponse(plans=plans, work_orders=work_orders)

    async def get_health(self, equipment_id: str) -> HealthResponse | None:
        """获取设备健康评分"""
        eq = get_equipment_by_id(equipment_id)
        if not eq:
            return None

        health = get_health_data(equipment_id)

        return HealthResponse(
            equipment_id=equipment_id,
            health_index=health["health_index"],
            assessment_date=health["assessment_date"],
            indicators=health["indicators"],
            trend=health["trend"],
            assessment_result=health["assessment_result"],
            recommendation=health["recommendation"],
        )

    def _get_recommended_actions(self, eq: dict, health_index: float, health_data: dict) -> list[str]:
        """根据设备类型和健康状态生成建议措施"""
        actions = []

        # 根据健康指数
        if health_index < 50:
            actions.append("全面绝缘检测（含介损、绝缘电阻、局放）")
            actions.append("油色谱分析并计算产气速率")
            actions.append("评估是否需要更换设备")
        elif health_index < 70:
            actions.append("专项绝缘检测")
            actions.append("DGA检测并对比历史数据")
            actions.append("红外热成像检测")
        elif health_index < 90:
            actions.append("预防性试验")
            actions.append("外观检查及清扫")
        else:
            actions.append("常规巡检")

        # 根据设备类型补充
        eq_type = eq.get("type", "")
        if eq_type == "transformer":
            if health_index < 80:
                actions.append("绕组直流电阻测试")
            actions.append("油位及密封检查")
        elif eq_type == "breaker":
            actions.append("机械特性测试（分合闸时间、速度）")
            actions.append("SF6气体压力及微水检测")
        elif eq_type == "gis":
            actions.append("SF6气体含水量检测")
            actions.append("UHF局部放电检测")

        # 根据指标异常补充
        indicators = health_data.get("indicators", {})
        for key, ind in indicators.items():
            if isinstance(ind, dict) and ind.get("status") == "异常":
                actions.append(f"针对{ind['name']}异常的专项检查：{ind['details']}")

        return actions[:6]  # 最多6条
