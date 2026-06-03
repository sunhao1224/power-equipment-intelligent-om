"""In-memory data store for the Hermes Agent demo."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import Any
from uuid import uuid4


class MockStore:
    def __init__(self) -> None:
        self.equipment = [
            {"equipment_id": "EQ-TR-001", "name": "1号主变压器", "type": "Transformer", "manufacturer": "华北电气", "model": "SZ11-50000/110", "batch_no": "TR-2021-A17", "location": "清河变电站", "voltage_level": "110kV", "commissioned_at": "2021-09-18", "health_score": 72, "risk_level": "important"},
            {"equipment_id": "EQ-MT-018", "name": "A区计量表箱 018", "type": "SmartMeter", "manufacturer": "志翔计量", "model": "ZX-MT-2024", "batch_no": "MT-2024-Q2", "location": "海淀台区 A", "voltage_level": "0.4kV", "commissioned_at": "2024-05-12", "health_score": 81, "risk_level": "normal"},
            {"equipment_id": "EQ-CB-006", "name": "110kV 断路器 006", "type": "CircuitBreaker", "manufacturer": "华东开关", "model": "LW36-126", "batch_no": "CB-2020-LW36", "location": "清河变电站", "voltage_level": "110kV", "commissioned_at": "2020-11-03", "health_score": 76, "risk_level": "medium"},
        ]
        self.events = [
            {"event_id": "EV-DGA-001", "equipment_id": "EQ-TR-001", "title": "DGA 乙炔持续升高", "event_type": "mock_event", "priority": "urgent", "time_window": "24h", "sensor_data": {"oil_temperature": 78.5, "winding_temperature": 86.2, "dga_h2": 215, "dga_ch4": 68, "dga_c2h2": 3.8, "dga_c2h4": 42, "load_rate": 0.86}, "summary": "乙炔和氢气同步升高，油温高于注意值，疑似内部放电风险。"},
            {"event_id": "EV-MT-002", "equipment_id": "EQ-MT-018", "title": "电能表误差漂移异常", "event_type": "mock_event", "priority": "important", "time_window": "7d", "sensor_data": {"meter_error": 1.12, "voltage": 226.4, "current": 18.6, "temperature": 43.1, "communication_loss_rate": 0.04}, "summary": "计量误差连续 7 日上升，需下钻采样回路和计量芯片风险。"},
        ]
        self.evidence = [
            {"evidence_id": "EVR-001", "title": "DL/T 722 DGA 高能放电判据", "source_type": "regulation", "source_id": "DLT-722-5.3", "content": "乙炔 C2H2 异常升高通常与高能放电或电弧放电风险相关，应结合氢气、总烃和温升趋势复核。", "confidence": 0.94, "linked_nodes": ["Transformer", "DGA", "C2H2", "ArcDischarge"], "tags": ["规程", "DGA", "放电"]},
            {"evidence_id": "EVR-002", "title": "相似案例：绕组引线接触不良导致放电", "source_type": "case", "source_id": "CASE-TR-2024-009", "content": "同型号变压器曾出现 C2H2 与 H2 同步升高，经停电检查定位为绕组引线连接点局部放电。", "confidence": 0.88, "linked_nodes": ["Transformer", "Winding", "LeadConnection", "PartialDischarge"], "tags": ["案例", "相似故障", "绕组"]},
            {"evidence_id": "EVR-003", "title": "设备部件图谱路径", "source_type": "graph", "source_id": "KG-PATH-TR-001", "content": "主变压器 has_part 绕组，绕组 has_part 绝缘纸板与引线连接点，二者均与放电和绝缘劣化存在关联。", "confidence": 0.9, "linked_nodes": ["Transformer", "Winding", "InsulationBoard", "LeadConnection"], "tags": ["图谱", "元器件"]},
            {"evidence_id": "EVR-004", "title": "同批次设备风险聚类", "source_type": "timeseries", "source_id": "BATCH-TR-2021-A17", "content": "同批次 8 台设备中 3 台近期出现油温或 DGA 趋势异常，风险集中于高负荷运行场景。", "confidence": 0.82, "linked_nodes": ["Batch", "Transformer", "LoadRate", "DGA"], "tags": ["批次", "趋势"]},
            {"evidence_id": "EVR-005", "title": "电能表误差漂移元器件路径", "source_type": "graph", "source_id": "KG-PATH-MT-018", "content": "电能表误差漂移可沿采样电阻、计量芯片、电源模块和温度补偿回路进行元器件级排查。", "confidence": 0.86, "linked_nodes": ["SmartMeter", "SamplingResistor", "MeteringChip", "PowerModule"], "tags": ["计量", "元器件"]},
        ]
        self.batch_items = [
            {"equipment_id": "EQ-TR-001", "equipment_name": "1号主变压器", "manufacturer": "华北电气", "model": "SZ11-50000/110", "batch_no": "TR-2021-A17", "location": "清河变电站", "risk_level": "critical", "probability_6m": 0.18, "probability_12m": 0.31, "probability_24m": 0.47, "reason": "触发设备，DGA 与温升趋势均异常。"},
            {"equipment_id": "EQ-TR-014", "equipment_name": "14号备用变压器", "manufacturer": "华北电气", "model": "SZ11-50000/110", "batch_no": "TR-2021-A17", "location": "昌平变电站", "risk_level": "high", "probability_6m": 0.12, "probability_12m": 0.24, "probability_24m": 0.39, "reason": "同批次且长期高负荷运行，油温趋势偏高。"},
            {"equipment_id": "EQ-TR-021", "equipment_name": "21号主变压器", "manufacturer": "华北电气", "model": "SZ11-50000/110", "batch_no": "TR-2021-A17", "location": "顺义变电站", "risk_level": "medium", "probability_6m": 0.08, "probability_12m": 0.16, "probability_24m": 0.28, "reason": "同批次设备，暂无 DGA 超限但负荷波动较大。"},
        ]
        self.diagnoses: dict[str, dict[str, Any]] = {}
        self.traces: dict[str, dict[str, Any]] = {}
        self.reports: dict[str, dict[str, Any]] = {}

    def list_equipment(self) -> list[dict[str, Any]]:
        return deepcopy(self.equipment)

    def get_equipment(self, equipment_id: str) -> dict[str, Any] | None:
        return deepcopy(next((item for item in self.equipment if item["equipment_id"] == equipment_id), None))

    def list_events(self) -> list[dict[str, Any]]:
        return deepcopy(self.events)

    def get_event(self, event_id: str | None) -> dict[str, Any] | None:
        if not event_id:
            return deepcopy(self.events[0])
        return deepcopy(next((item for item in self.events if item["event_id"] == event_id), None))

    def list_evidence(self, query: str | None = None) -> list[dict[str, Any]]:
        rows = deepcopy(self.evidence)
        if query:
            q = query.lower()
            rows = [item for item in rows if q in item["title"].lower() or q in item["content"].lower() or any(q in tag.lower() for tag in item["tags"])]
        return rows

    def create_diagnosis(self, payload: dict[str, Any]) -> dict[str, Any]:
        diagnosis_id = f"diag_{uuid4().hex[:8]}"
        orchestrator_id = f"orch_{uuid4().hex[:8]}"
        trace_id = f"trace_{uuid4().hex[:8]}"
        task = {"diagnosis_id": diagnosis_id, "orchestrator_id": orchestrator_id, "agent_trace_id": trace_id, "status": "pending", "input": payload, "agents_output": [], "report": None, "review_findings": []}
        self.diagnoses[diagnosis_id] = task
        self.traces[trace_id] = {"trace_id": trace_id, "diagnosis_id": diagnosis_id, "orchestrator_id": orchestrator_id, "status": "pending", "started_at": datetime.now(), "completed_at": None, "agent_steps": [], "tool_calls": [], "skill_calls": [], "evidence_links": []}
        return deepcopy(task)

    def update_task(self, diagnosis_id: str, **fields: Any) -> dict[str, Any] | None:
        task = self.diagnoses.get(diagnosis_id)
        if not task:
            return None
        task.update(fields)
        return deepcopy(task)

    def get_task(self, diagnosis_id: str) -> dict[str, Any] | None:
        return deepcopy(self.diagnoses.get(diagnosis_id))

    def get_trace(self, trace_id: str) -> dict[str, Any] | None:
        return deepcopy(self.traces.get(trace_id))

    def set_trace(self, trace_id: str, trace: dict[str, Any]) -> None:
        self.traces[trace_id] = deepcopy(trace)

    def save_report(self, report: dict[str, Any]) -> None:
        self.reports[report["report_id"]] = deepcopy(report)

    def list_reports(self) -> list[dict[str, Any]]:
        return sorted(deepcopy(list(self.reports.values())), key=lambda item: item["created_at"], reverse=True)

    def get_report(self, report_id: str) -> dict[str, Any] | None:
        return deepcopy(self.reports.get(report_id))


store = MockStore()
