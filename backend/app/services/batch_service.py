"""批次评估服务"""
import random
from datetime import datetime

from app.models.batch import (
    BatchAssessRequest,
    BatchAssessResponse,
    RiskDevice,
    BatchReport,
)
from app.mock_data.equipment import get_equipment_by_id, EQUIPMENT_LIST
from app.mock_data.faults import get_fault_case_by_equipment


class BatchService:
    """批次评估服务"""

    async def assess(self, request: BatchAssessRequest) -> BatchAssessResponse:
        """执行批次评估"""
        trigger_eq = get_equipment_by_id(request.equipment_id)
        if not trigger_eq:
            # 使用默认值
            trigger_eq = {
                "manufacturer": "特变电工",
                "model": "SFZ11",
                "type": "transformer",
                "type_name": "变压器",
            }

        # 按条件匹配批次设备
        criteria = request.batch_criteria
        batch_devices = []
        for eq in EQUIPMENT_LIST:
            match = True
            if criteria.get("manufacturer", True) and eq["manufacturer"] != trigger_eq.get("manufacturer"):
                match = False
            if criteria.get("model", True):
                # 型号前缀匹配（同系列）
                trigger_model = trigger_eq.get("model", "")[:8]
                if not eq["model"].startswith(trigger_model):
                    match = False
            if criteria.get("year", True):
                # 投运年份相近（5年内）
                try:
                    eq_year = int(eq["commission_date"][:4])
                    trigger_year = int(trigger_eq.get("commission_date", "2015")[:4])
                    if abs(eq_year - trigger_year) > 5:
                        match = False
                except (ValueError, KeyError):
                    pass
            if match:
                batch_devices.append(eq)

        # 评估风险
        risk_devices = []
        health_scores = []
        for eq in batch_devices:
            health_scores.append(eq["health_index"])
            if eq["health_index"] < 85:
                # 检查是否有故障历史
                fault_cases = get_fault_case_by_equipment(eq["equipment_id"])
                issue = "健康指数偏低"
                if fault_cases:
                    issue = f"曾发生{fault_cases[0]['fault_type']}故障"

                risk_level = "高" if eq["health_index"] < 60 else "中"
                risk_score = round((100 - eq["health_index"]) / 100 * random.uniform(0.8, 1.2), 2)

                risk_devices.append(RiskDevice(
                    equipment_id=eq["equipment_id"],
                    name=eq["name"],
                    health_index=eq["health_index"],
                    risk_level=risk_level,
                    risk_score=min(1.0, risk_score),
                    issue_description=issue,
                ))

        # 统计分析
        avg_health = round(sum(health_scores) / len(health_scores), 1) if health_scores else 0
        std_health = 0
        if len(health_scores) > 1:
            variance = sum((h - avg_health) ** 2 for h in health_scores) / len(health_scores)
            std_health = round(variance ** 0.5, 1)

        # 故障统计
        fault_count = 0
        fault_types = {}
        for eq in batch_devices:
            cases = get_fault_case_by_equipment(eq["equipment_id"])
            for c in cases:
                fault_count += 1
                ft = c["fault_type"]
                fault_types[ft] = fault_types.get(ft, 0) + 1

        # 风险等级
        high_risk_count = len([r for r in risk_devices if r.risk_level == "高"])
        if high_risk_count >= 2:
            batch_risk_level = "高"
        elif high_risk_count >= 1 or len(risk_devices) >= 2:
            batch_risk_level = "中"
        else:
            batch_risk_level = "低"

        # 生成建议
        recommendations = []
        if batch_risk_level == "高":
            recommendations.append("建议对同批次所有设备进行专项检测")
            recommendations.append("重点关注健康指数低于70分的设备")
            recommendations.append("评估是否存在家族性缺陷，必要时启动批量更换计划")
        elif batch_risk_level == "中":
            recommendations.append("建议对风险设备安排专项检测")
            recommendations.append("缩短同批次设备巡检周期")
            recommendations.append("持续关注设备状态变化趋势")
        else:
            recommendations.append("同批次设备状态整体良好，保持正常巡检周期")
            recommendations.append("建议每季度进行一次批次状态评估")

        # 风险汇总
        risk_summary = {
            "high_risk": high_risk_count,
            "medium_risk": len([r for r in risk_devices if r.risk_level == "中"]),
            "low_risk": len(batch_devices) - len(risk_devices),
            "fault_history_count": fault_count,
            "fault_type_distribution": fault_types,
        }

        statistical_analysis = {
            "avg_health_index": avg_health,
            "std_health_index": std_health,
            "min_health_index": round(min(health_scores), 1) if health_scores else 0,
            "max_health_index": round(max(health_scores), 1) if health_scores else 0,
            "below_threshold_count": len([h for h in health_scores if h < 70]),
        }

        # 批次描述
        batch_desc = (
            f"{trigger_eq.get('manufacturer', '未知')}生产的"
            f"{trigger_eq.get('type_name', '设备')}同批次设备，"
            f"共{len(batch_devices)}台"
        )

        return BatchAssessResponse(
            batch_size=len(batch_devices),
            risk_devices=risk_devices,
            batch_report=BatchReport(
                batch_description=batch_desc,
                total_count=len(batch_devices),
                risk_summary=risk_summary,
                statistical_analysis=statistical_analysis,
                recommendations=recommendations,
                risk_level=batch_risk_level,
            ),
        )
