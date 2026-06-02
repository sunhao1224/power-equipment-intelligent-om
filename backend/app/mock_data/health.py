"""健康评分 Mock 数据"""
import math
import random
from datetime import datetime, timedelta
from typing import Optional


def get_health_data(equipment_id: str) -> dict:
    """获取设备健康评分数据"""

    # 各设备的健康指标配置
    health_profiles = {
        "TR-001": {
            "health_index": 92.5,
            "indicators": {
                "insulation": {"score": 94, "weight": 0.4, "name": "绝缘状态", "status": "优良",
                               "details": "介损0.35%，绝缘电阻合格，DGA正常"},
                "thermal": {"score": 91, "weight": 0.25, "name": "热状态", "status": "优良",
                            "details": "油温正常，温升在标准范围内"},
                "electrical": {"score": 93, "weight": 0.25, "name": "电气性能", "status": "优良",
                               "details": "直流电阻平衡，短路阻抗正常"},
                "mechanical": {"score": 90, "weight": 0.1, "name": "机械性能", "status": "优良",
                               "details": "振动正常，无异常声响"},
            },
        },
        "TR-002": {
            "health_index": 78.3,
            "indicators": {
                "insulation": {"score": 72, "weight": 0.4, "name": "绝缘状态", "status": "注意",
                               "details": "DGA总烃接近注意值，C2H2检出，需持续关注"},
                "thermal": {"score": 75, "weight": 0.25, "name": "热状态", "status": "注意",
                            "details": "油温偏高，近期有上升趋势"},
                "electrical": {"score": 85, "weight": 0.25, "name": "电气性能", "status": "合格",
                               "details": "直流电阻A相偏差1.8%，接近注意值"},
                "mechanical": {"score": 82, "weight": 0.1, "name": "机械性能", "status": "合格",
                               "details": "振动略高于正常值"},
            },
        },
        "TR-003": {
            "health_index": 95.2,
            "indicators": {
                "insulation": {"score": 96, "weight": 0.4, "name": "绝缘状态", "status": "优良",
                               "details": "各项绝缘指标优良，DGA数据正常"},
                "thermal": {"score": 95, "weight": 0.25, "name": "热状态", "status": "优良",
                            "details": "油温正常，冷却系统运行良好"},
                "electrical": {"score": 94, "weight": 0.25, "name": "电气性能", "status": "优良",
                               "details": "电气试验数据均在标准范围内"},
                "mechanical": {"score": 95, "weight": 0.1, "name": "机械性能", "status": "优良",
                               "details": "运行平稳，振动数据优良"},
            },
        },
        "TR-004": {
            "health_index": 68.7,
            "indicators": {
                "insulation": {"score": 58, "weight": 0.4, "name": "绝缘状态", "status": "异常",
                               "details": "套管介损超标(1.2%)，DGA异常，需尽快处理"},
                "thermal": {"score": 65, "weight": 0.25, "name": "热状态", "status": "注意",
                            "details": "油温持续偏高，温升接近限值"},
                "electrical": {"score": 78, "weight": 0.25, "name": "电气性能", "status": "合格",
                               "details": "直流电阻正常，但短路阻抗有轻微变化"},
                "mechanical": {"score": 75, "weight": 0.1, "name": "机械性能", "status": "合格",
                               "details": "振动略大，需关注"},
            },
        },
        "TR-005": {
            "health_index": 97.8,
            "indicators": {
                "insulation": {"score": 98, "weight": 0.4, "name": "绝缘状态", "status": "优良",
                               "details": "新投运设备，各项绝缘指标优良"},
                "thermal": {"score": 97, "weight": 0.25, "name": "热状态", "status": "优良",
                            "details": "油温正常，负荷率低"},
                "electrical": {"score": 98, "weight": 0.25, "name": "电气性能", "status": "优良",
                               "details": "出厂试验数据优良"},
                "mechanical": {"score": 98, "weight": 0.1, "name": "机械性能", "status": "优良",
                               "details": "运行平稳无异常"},
            },
        },
        "CB-001": {
            "health_index": 88.9,
            "indicators": {
                "mechanical": {"score": 85, "weight": 0.35, "name": "机械性能", "status": "合格",
                               "details": "操动机构曾检修，目前运行正常"},
                "insulation": {"score": 92, "weight": 0.3, "name": "绝缘性能", "status": "优良",
                               "details": "SF6微水含量合格，绝缘电阻正常"},
                "electrical": {"score": 90, "weight": 0.25, "name": "电气性能", "status": "优良",
                               "details": "主回路电阻正常，分合闸时间合格"},
                "sealing": {"score": 88, "weight": 0.1, "name": "密封性能", "status": "合格",
                            "details": "SF6压力正常，年泄漏率合格"},
            },
        },
        "CB-002": {
            "health_index": 91.2,
            "indicators": {
                "mechanical": {"score": 90, "weight": 0.35, "name": "机械性能", "status": "优良",
                               "details": "操动机构运行正常，动作次数在安全范围"},
                "insulation": {"score": 93, "weight": 0.3, "name": "绝缘性能", "status": "优良",
                               "details": "SF6气体质量良好"},
                "electrical": {"score": 91, "weight": 0.25, "name": "电气性能", "status": "优良",
                               "details": "分合闸特性优良"},
                "sealing": {"score": 92, "weight": 0.1, "name": "密封性能", "status": "优良",
                            "details": "SF6压力稳定"},
            },
        },
        "CB-003": {
            "health_index": 45.2,
            "indicators": {
                "mechanical": {"score": 40, "weight": 0.35, "name": "机械性能", "status": "异常",
                               "details": "分闸时间超标，操动机构需检修"},
                "insulation": {"score": 55, "weight": 0.3, "name": "绝缘性能", "status": "注意",
                               "details": "SF6压力偏低，需检查泄漏点"},
                "electrical": {"score": 48, "weight": 0.25, "name": "电气性能", "status": "异常",
                               "details": "主回路电阻超标，需处理"},
                "sealing": {"score": 38, "weight": 0.1, "name": "密封性能", "status": "异常",
                            "details": "SF6泄漏率超标，需更换密封件"},
            },
        },
        "GIS-001": {
            "health_index": 96.1,
            "indicators": {
                "insulation": {"score": 97, "weight": 0.4, "name": "绝缘状态", "status": "优良",
                               "details": "SF6微水合格，局放检测正常"},
                "mechanical": {"score": 95, "weight": 0.25, "name": "机械性能", "status": "优良",
                               "details": "各元件动作正常"},
                "sealing": {"score": 96, "weight": 0.25, "name": "密封性能", "status": "优良",
                            "details": "各气室压力正常"},
                "monitoring": {"score": 96, "weight": 0.1, "name": "在线监测", "status": "优良",
                               "details": "在线监测装置运行正常"},
            },
        },
        "GIS-002": {
            "health_index": 89.5,
            "indicators": {
                "insulation": {"score": 88, "weight": 0.4, "name": "绝缘状态", "status": "合格",
                               "details": "曾发现局放异常，已处理，需持续监测"},
                "mechanical": {"score": 90, "weight": 0.25, "name": "机械性能", "status": "优良",
                               "details": "各元件运行正常"},
                "sealing": {"score": 91, "weight": 0.25, "name": "密封性能", "status": "优良",
                            "details": "气室压力正常"},
                "monitoring": {"score": 89, "weight": 0.1, "name": "在线监测", "status": "合格",
                               "details": "UHF在线监测装置已加装"},
            },
        },
        "GIS-003": {
            "health_index": 85.3,
            "indicators": {
                "insulation": {"score": 84, "weight": 0.4, "name": "绝缘状态", "status": "合格",
                               "details": "检修中，等待绝缘复测"},
                "mechanical": {"score": 86, "weight": 0.25, "name": "机械性能", "status": "合格",
                               "details": "部分隔离开关需润滑"},
                "sealing": {"score": 87, "weight": 0.25, "name": "密封性能", "status": "合格",
                            "details": "个别气室需检漏"},
                "monitoring": {"score": 85, "weight": 0.1, "name": "在线监测", "status": "合格",
                               "details": "在线监测装置需校准"},
            },
        },
        "CB-004": {
            "health_index": 94.6,
            "indicators": {
                "mechanical": {"score": 95, "weight": 0.35, "name": "机械性能", "status": "优良",
                               "details": "ABB设备，运行状态优良"},
                "insulation": {"score": 94, "weight": 0.3, "name": "绝缘性能", "status": "优良",
                               "details": "SF6气体质量优良"},
                "electrical": {"score": 95, "weight": 0.25, "name": "电气性能", "status": "优良",
                               "details": "分合闸特性优良"},
                "sealing": {"score": 95, "weight": 0.1, "name": "密封性能", "status": "优良",
                            "details": "SF6压力稳定"},
            },
        },
    }

    profile = health_profiles.get(equipment_id, health_profiles["TR-001"])

    # 生成历史趋势
    now = datetime.now()
    trend_data = []
    base_health = profile["health_index"]

    for i in range(12, 0, -1):
        t = now - timedelta(days=i * 30)
        # 模拟健康度缓慢变化
        drift = random.uniform(-2, 1) if base_health < 80 else random.uniform(-1, 0.5)
        base_health = max(30, min(100, base_health + drift))
        trend_data.append({
            "date": t.strftime("%Y-%m"),
            "health_index": round(base_health, 1),
        })

    # 最后一点为当前值
    trend_data.append({
        "date": now.strftime("%Y-%m"),
        "health_index": profile["health_index"],
    })

    return {
        "equipment_id": equipment_id,
        "health_index": profile["health_index"],
        "assessment_date": now.strftime("%Y-%m-%d"),
        "indicators": profile["indicators"],
        "trend": trend_data,
        "assessment_result": _get_assessment_result(profile["health_index"]),
        "recommendation": _get_recommendation(profile["health_index"]),
    }


def _get_assessment_result(health_index: float) -> str:
    """根据健康指数获取评估等级"""
    if health_index >= 90:
        return "优良"
    elif health_index >= 70:
        return "合格"
    elif health_index >= 50:
        return "注意"
    else:
        return "异常"


def _get_recommendation(health_index: float) -> str:
    """根据健康指数获取维护建议"""
    if health_index >= 90:
        return "设备状态优良，可按正常周期安排检修。建议持续关注关键指标变化趋势。"
    elif health_index >= 70:
        return "设备状态合格，建议缩短检测周期，加强在线监测，关注异常指标发展趋势。"
    elif health_index >= 50:
        return "设备状态需关注，建议尽快安排专项检测，制定针对性维护方案，考虑列入近期检修计划。"
    else:
        return "设备状态异常，建议立即申请停电检修，进行全面检查和缺陷处理，评估是否需要更换。"
