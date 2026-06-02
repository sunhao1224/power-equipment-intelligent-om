"""传感器时序 Mock 数据"""
import math
import random
from datetime import datetime, timedelta
from typing import Optional


def _generate_time_series(
    days: int = 30,
    interval_hours: int = 1,
    base_value: float = 50.0,
    amplitude: float = 10.0,
    noise: float = 2.0,
    trend: float = 0.0,
) -> list[dict]:
    """生成模拟时序数据"""
    data = []
    now = datetime.now()
    start = now - timedelta(days=days)
    points = int(days * 24 / interval_hours)

    for i in range(points):
        t = start + timedelta(hours=i * interval_hours)
        # 日周期波动
        hour_factor = math.sin(2 * math.pi * t.hour / 24)
        # 趋势
        trend_value = trend * i / points
        # 随机噪声
        noise_value = random.uniform(-noise, noise)
        value = base_value + amplitude * hour_factor + trend_value + noise_value

        data.append({
            "timestamp": t.isoformat(),
            "value": round(value, 2),
        })

    return data


def get_sensor_data(
    equipment_id: str,
    sensor_type: str = "oil_temperature",
    days: int = 30,
) -> dict:
    """获取传感器时序数据"""

    sensor_configs = {
        "TR-001": {
            "oil_temperature": {"base": 55.0, "amplitude": 8.0, "noise": 1.5, "trend": 0.5, "unit": "°C"},
            "winding_temperature": {"base": 68.0, "amplitude": 12.0, "noise": 2.0, "trend": 0.8, "unit": "°C"},
            "load_current": {"base": 220.0, "amplitude": 60.0, "noise": 10.0, "trend": 0.0, "unit": "A"},
            "vibration": {"base": 2.5, "amplitude": 0.8, "noise": 0.3, "trend": 0.1, "unit": "mm/s"},
        },
        "TR-002": {
            "oil_temperature": {"base": 62.0, "amplitude": 10.0, "noise": 2.0, "trend": 3.0, "unit": "°C"},
            "winding_temperature": {"base": 75.0, "amplitude": 15.0, "noise": 3.0, "trend": 4.0, "unit": "°C"},
            "load_current": {"base": 240.0, "amplitude": 70.0, "noise": 12.0, "trend": 5.0, "unit": "A"},
            "vibration": {"base": 3.8, "amplitude": 1.2, "noise": 0.5, "trend": 0.5, "unit": "mm/s"},
        },
        "TR-003": {
            "oil_temperature": {"base": 50.0, "amplitude": 7.0, "noise": 1.0, "trend": 0.0, "unit": "°C"},
            "winding_temperature": {"base": 63.0, "amplitude": 10.0, "noise": 1.5, "trend": 0.0, "unit": "°C"},
            "load_current": {"base": 280.0, "amplitude": 80.0, "noise": 15.0, "trend": 0.0, "unit": "A"},
            "vibration": {"base": 2.0, "amplitude": 0.5, "noise": 0.2, "trend": 0.0, "unit": "mm/s"},
        },
        "TR-004": {
            "oil_temperature": {"base": 65.0, "amplitude": 12.0, "noise": 3.0, "trend": 5.0, "unit": "°C"},
            "winding_temperature": {"base": 78.0, "amplitude": 18.0, "noise": 4.0, "trend": 6.0, "unit": "°C"},
            "load_current": {"base": 350.0, "amplitude": 90.0, "noise": 20.0, "trend": 10.0, "unit": "A"},
            "vibration": {"base": 4.5, "amplitude": 1.8, "noise": 0.8, "trend": 1.0, "unit": "mm/s"},
        },
        "TR-005": {
            "oil_temperature": {"base": 48.0, "amplitude": 6.0, "noise": 1.0, "trend": 0.0, "unit": "°C"},
            "winding_temperature": {"base": 60.0, "amplitude": 8.0, "noise": 1.0, "trend": 0.0, "unit": "°C"},
            "load_current": {"base": 150.0, "amplitude": 40.0, "noise": 8.0, "trend": 0.0, "unit": "A"},
            "vibration": {"base": 1.8, "amplitude": 0.4, "noise": 0.15, "trend": 0.0, "unit": "mm/s"},
        },
    }

    # 默认配置
    default_config = {
        "oil_temperature": {"base": 55.0, "amplitude": 8.0, "noise": 1.5, "trend": 0.0, "unit": "°C"},
        "winding_temperature": {"base": 68.0, "amplitude": 12.0, "noise": 2.0, "trend": 0.0, "unit": "°C"},
        "load_current": {"base": 200.0, "amplitude": 50.0, "noise": 10.0, "trend": 0.0, "unit": "A"},
        "vibration": {"base": 2.5, "amplitude": 0.8, "noise": 0.3, "trend": 0.0, "unit": "mm/s"},
    }

    config_map = sensor_configs.get(equipment_id, default_config)
    config = config_map.get(sensor_type, default_config.get(sensor_type, default_config["oil_temperature"]))

    time_series = _generate_time_series(
        days=days,
        base_value=config["base"],
        amplitude=config["amplitude"],
        noise=config["noise"],
        trend=config["trend"],
    )

    return {
        "equipment_id": equipment_id,
        "sensor_type": sensor_type,
        "unit": config["unit"],
        "data_points": len(time_series),
        "start_time": time_series[0]["timestamp"] if time_series else None,
        "end_time": time_series[-1]["timestamp"] if time_series else None,
        "statistics": {
            "min": round(min(d["value"] for d in time_series), 2) if time_series else 0,
            "max": round(max(d["value"] for d in time_series), 2) if time_series else 0,
            "avg": round(sum(d["value"] for d in time_series) / len(time_series), 2) if time_series else 0,
            "current": time_series[-1]["value"] if time_series else 0,
        },
        "data": time_series,
    }


def get_dga_data(equipment_id: str, history_count: int = 12) -> dict:
    """获取 DGA（溶解气体分析）数据"""

    # 各设备的 DGA 数据特征 (ppm)
    dga_profiles = {
        "TR-001": {
            "H2": (25, 5, 0.2), "CH4": (30, 8, 0.5), "C2H2": (2, 1, 0.1),
            "C2H4": (35, 10, 0.3), "C2H6": (20, 5, 0.2), "CO": (200, 50, 5.0),
            "CO2": (1500, 300, 20.0),
        },
        "TR-002": {
            "H2": (45, 15, 2.0), "CH4": (55, 20, 3.0), "C2H2": (8, 4, 1.5),
            "C2H4": (70, 25, 5.0), "C2H6": (40, 15, 2.0), "CO": (350, 100, 15.0),
            "CO2": (2500, 500, 50.0),
        },
        "TR-003": {
            "H2": (18, 3, 0.1), "CH4": (22, 5, 0.2), "C2H2": (1, 0.5, 0.0),
            "C2H4": (25, 6, 0.2), "C2H6": (15, 3, 0.1), "CO": (150, 30, 2.0),
            "CO2": (1200, 200, 10.0),
        },
        "TR-004": {
            "H2": (65, 25, 5.0), "CH4": (80, 30, 8.0), "C2H2": (15, 8, 3.0),
            "C2H4": (110, 40, 12.0), "C2H6": (55, 20, 5.0), "CO": (500, 150, 30.0),
            "CO2": (3500, 800, 80.0),
        },
        "TR-005": {
            "H2": (12, 2, 0.0), "CH4": (15, 3, 0.1), "C2H2": (0.5, 0.3, 0.0),
            "C2H4": (18, 4, 0.1), "C2H6": (10, 2, 0.1), "CO": (120, 20, 1.0),
            "CO2": (1000, 150, 5.0),
        },
    }

    profile = dga_profiles.get(equipment_id, dga_profiles["TR-001"])

    now = datetime.now()
    records = []
    for i in range(history_count, 0, -1):
        sample_date = now - timedelta(days=i * 30)
        record = {"sample_date": sample_date.strftime("%Y-%m-%d")}
        for gas, (base, amplitude, trend) in profile.items():
            noise_val = random.uniform(-amplitude * 0.3, amplitude * 0.3)
            trend_val = trend * (history_count - i)
            value = max(0, base + trend_val + noise_val)
            record[gas] = round(value, 2)

        # 计算总烃
        record["total_hydrocarbon"] = round(
            record["CH4"] + record["C2H2"] + record["C2H4"] + record["C2H6"], 2
        )
        records.append(record)

    latest = records[-1] if records else {}

    # 三比值法诊断
    diagnosis = _three_ratio_diagnosis(latest)

    return {
        "equipment_id": equipment_id,
        "records": records,
        "latest": latest,
        "diagnosis": diagnosis,
        "attention_thresholds": {
            "H2": 150, "CH4": 100, "C2H2": 5,
            "C2H4": 100, "C2H6": 100, "CO": 700,
            "CO2": 5000, "total_hydrocarbon": 150,
        },
    }


def _three_ratio_diagnosis(dga: dict) -> dict:
    """IEC 三比值法诊断"""
    if not dga:
        return {"result": "数据不足", "code": "N/A"}

    c2h2 = dga.get("C2H2", 0)
    c2h4 = dga.get("C2H4", 0)
    ch4 = dga.get("CH4", 0)
    h2 = dga.get("H2", 0)
    c2h6 = dga.get("C2H6", 0)

    # 比值计算
    r1 = c2h2 / c2h4 if c2h4 > 0 else 0
    r2 = ch4 / h2 if h2 > 0 else 0
    r3 = c2h4 / c2h6 if c2h6 > 0 else 0

    # 简化判断
    if r1 < 0.1 and r2 > 1.0 and r3 < 1.0:
        return {"result": "正常老化", "code": "0-1-0", "severity": "low"}
    elif r1 > 0.1 and r1 < 3.0 and r2 < 1.0:
        return {"result": "电弧放电", "code": "1-0-2", "severity": "high"}
    elif r1 < 0.1 and r2 < 1.0 and r3 > 3.0:
        return {"result": "低温过热（<150°C）", "code": "0-0-1", "severity": "medium"}
    elif r1 < 0.1 and r2 > 1.0 and r3 > 3.0:
        return {"result": "高温过热（>700°C）", "code": "0-2-2", "severity": "high"}
    else:
        return {"result": "局部放电", "code": "0-1-0", "severity": "medium"}


def get_partial_discharge_data(equipment_id: str, days: int = 7) -> dict:
    """获取局部放电数据"""
    random.seed(hash(equipment_id) % 2**32)

    now = datetime.now()
    data = []
    base_pd = {"TR-001": 50, "TR-002": 180, "TR-003": 30, "TR-004": 350, "TR-005": 20}
    base = base_pd.get(equipment_id, 80)

    for i in range(days * 24):
        t = now - timedelta(hours=days * 24 - i)
        # 随机脉冲
        pd_value = base + random.uniform(-base * 0.3, base * 0.5)
        if random.random() < 0.05:
            pd_value *= 3  # 偶尔出现大幅值脉冲

        data.append({
            "timestamp": t.isoformat(),
            "pd_magnitude": round(pd_value, 1),
            "pd_count": random.randint(0, 20) if pd_value > base else random.randint(0, 5),
            "phase_angle": round(random.uniform(0, 360), 1),
        })

    # PRPD 谱图数据（简化）
    prpd = []
    for phase_bin in range(0, 360, 10):
        count = random.randint(0, 50) if phase_bin in range(30, 90) or phase_bin in range(210, 270) else random.randint(0, 5)
        max_magnitude = base * (2.5 if count > 20 else 1.0) * random.uniform(0.5, 1.5)
        prpd.append({
            "phase": phase_bin,
            "count": count,
            "max_magnitude": round(max_magnitude, 1),
        })

    return {
        "equipment_id": equipment_id,
        "period_days": days,
        "summary": {
            "max_magnitude": round(max(d["pd_magnitude"] for d in data), 1) if data else 0,
            "avg_magnitude": round(sum(d["pd_magnitude"] for d in data) / len(data), 1) if data else 0,
            "total_pd_count": sum(d["pd_count"] for d in data),
            "trend": "上升" if base > 100 else "平稳",
            "risk_level": "高" if base > 200 else ("中" if base > 80 else "低"),
        },
        "prpd_spectrum": prpd,
        "time_series": data[-72:],  # 最近 3 天
    }
