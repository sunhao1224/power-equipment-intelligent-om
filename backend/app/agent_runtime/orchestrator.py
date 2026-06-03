"""Hermes Agent orchestration simulator.

The runtime is deterministic on purpose: it behaves like a production Agent
service from the API and WebSocket perspective, while staying fully local for
the course demo.
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any, AsyncIterator
from uuid import uuid4

from app.repositories.mock import store


AGENT_BLUEPRINTS = [
    ("data_sensing", "Data Sensing Agent", "数据理解与特征解释"),
    ("knowledge_retrieval", "Knowledge Retrieval Agent", "RAG 与知识图谱证据检索"),
    ("rca", "RCA Agent", "元器件级根因分析"),
    ("batch_lifetime", "Batch Lifetime Agent", "批次寿命与风险预测"),
    ("fmea", "FMEA Agent", "失效模式与 RPN 评分"),
    ("decision", "Decision Agent", "处置策略与工单草稿"),
    ("review", "Review Agent", "事实性、完整性与合规审核"),
]


class ChiefDiagnosisOrchestrator:
    def _event(self, event_type: str, diagnosis_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "event_type": event_type,
            "diagnosis_id": diagnosis_id,
            "timestamp": datetime.now().isoformat(),
            "payload": payload,
        }

    async def stream(self, diagnosis_id: str) -> AsyncIterator[dict[str, Any]]:
        task = store.get_task(diagnosis_id)
        if not task:
            yield self._event("diagnosis_failed", diagnosis_id, {"message": "诊断任务不存在"})
            return

        trace = store.get_trace(task["agent_trace_id"])
        if not trace:
            yield self._event("diagnosis_failed", diagnosis_id, {"message": "Trace 不存在"})
            return

        if task["status"] == "completed":
            yield self._event("diagnosis_done", diagnosis_id, {"report": task["report"], "trace_id": task["agent_trace_id"]})
            return

        store.update_task(diagnosis_id, status="running")
        trace["status"] = "running"
        store.set_trace(trace["trace_id"], trace)

        subtasks = [{"agent_id": agent_id, "name": name, "role": role} for agent_id, name, role in AGENT_BLUEPRINTS]
        yield self._event("task_decomposed", diagnosis_id, {"orchestrator_id": task["orchestrator_id"], "subtasks": subtasks})

        evidence = store.list_evidence()
        agent_steps: list[dict[str, Any]] = []
        tool_calls: list[dict[str, Any]] = []
        skill_calls: list[dict[str, Any]] = []

        for index, (agent_id, name, role) in enumerate(AGENT_BLUEPRINTS):
            node = {
                "agent_id": agent_id,
                "name": name,
                "role": role,
                "status": "spawned",
                "progress": 0,
                "confidence": 0.0,
                "evidence_count": 0,
                "duration_ms": 0,
                "summary": "",
            }
            agent_steps.append(node)
            trace["agent_steps"] = agent_steps
            store.set_trace(trace["trace_id"], trace)
            yield self._event("agent_spawned", diagnosis_id, {"agent": node})

            for progress in (28, 64, 100):
                await asyncio.sleep(0.12)
                node["status"] = "running" if progress < 100 else "tool_calling"
                node["progress"] = progress
                yield self._event("agent_progress", diagnosis_id, {"agent_id": agent_id, "progress": progress, "message": self._progress_message(agent_id, progress)})

            call = self._tool_call(agent_id, index)
            tool_calls.append(call)
            trace["tool_calls"] = tool_calls
            store.set_trace(trace["trace_id"], trace)
            yield self._event("tool_call", diagnosis_id, {"tool_call": call})

            skill = self._skill_call(agent_id)
            skill_calls.append(skill)
            result = self._agent_result(agent_id, evidence)
            node.update(result)
            node["status"] = "completed"
            node["progress"] = 100
            trace["agent_steps"] = agent_steps
            trace["skill_calls"] = skill_calls
            trace["evidence_links"] = evidence
            store.set_trace(trace["trace_id"], trace)
            store.update_task(diagnosis_id, agents_output=agent_steps)
            yield self._event("agent_result", diagnosis_id, {"agent": node, "skill_call": skill})

        store.update_task(diagnosis_id, status="reviewing")
        yield self._event("aggregation_started", diagnosis_id, {"message": "Chief Orchestrator 正在聚合专家结论"})
        await asyncio.sleep(0.15)

        report = self._build_report(task, evidence)
        review_findings = report["review_findings"]
        trace["status"] = "completed"
        trace["completed_at"] = datetime.now()
        store.set_trace(trace["trace_id"], trace)
        store.save_report(report)
        store.update_task(diagnosis_id, status="completed", report=report, review_findings=review_findings, agents_output=agent_steps)

        yield self._event("review_completed", diagnosis_id, {"review_status": "passed", "findings": review_findings})
        yield self._event("diagnosis_done", diagnosis_id, {"report": report, "trace_id": trace["trace_id"]})

    def _progress_message(self, agent_id: str, progress: int) -> str:
        messages = {
            "data_sensing": "解析传感器快照与历史窗口",
            "knowledge_retrieval": "召回规程、案例和图谱子路径",
            "rca": "构造根因假设并进行证据加权",
            "batch_lifetime": "计算同批次设备寿命风险",
            "fmea": "评估失效模式的 S/O/D/RPN",
            "decision": "生成处置策略和工单草稿",
            "review": "审核事实引用、数值和合规性",
        }
        return f"{messages[agent_id]} · {progress}%"

    def _tool_call(self, agent_id: str, index: int) -> dict[str, Any]:
        tools = {
            "data_sensing": ("timeseries_query", "读取 24h 传感器窗口", "识别 DGA、油温、负荷三类异常特征"),
            "knowledge_retrieval": ("hybrid_rag_search", "混合检索规程、案例和图谱", "召回 5 条证据并激活 11 个图谱节点"),
            "rca": ("neo4j_graph_query", "沿 has_part/caused_by 下钻", "定位绕组、绝缘纸板、引线连接点"),
            "batch_lifetime": ("batch_risk_model", "查询同批次设备趋势", "输出 6/12/24 月风险概率"),
            "fmea": ("fmea_rpn_engine", "计算失效模式 RPN", "生成 3 个高优先级维护项"),
            "decision": ("workorder_tool", "生成工单草稿", "形成 4 条处置动作和安全要求"),
            "review": ("evidence_consistency_review", "校验报告证据链", "所有关键结论均绑定证据"),
        }
        tool_name, request, response = tools[agent_id]
        return {
            "call_id": f"tool_{uuid4().hex[:8]}",
            "agent_id": agent_id,
            "tool_name": tool_name,
            "request_summary": request,
            "response_summary": response,
            "latency_ms": 120 + index * 37,
            "status": "completed",
        }

    def _skill_call(self, agent_id: str) -> dict[str, Any]:
        skills = {
            "data_sensing": "sensor_semantic_summary",
            "knowledge_retrieval": "standard_clause_check",
            "rca": "dga_fault_analysis",
            "batch_lifetime": "batch_lifetime_prediction",
            "fmea": "fmea_rpn_scoring",
            "decision": "maintenance_workorder_generation",
            "review": "evidence_consistency_review",
        }
        return {"call_id": f"skill_{uuid4().hex[:8]}", "agent_id": agent_id, "skill_name": skills[agent_id], "skill_version": "v1", "status": "completed"}

    def _agent_result(self, agent_id: str, evidence: list[dict[str, Any]]) -> dict[str, Any]:
        results = {
            "data_sensing": ("DGA C2H2、H2 与油温呈同步上升，数据质量评分 96%。", 0.91, 2, 620),
            "knowledge_retrieval": ("召回 DL/T 722、相似案例和设备部件图谱路径。", 0.93, 5, 740),
            "rca": ("Top-1 根因为绕组引线连接点局部放电，置信度 0.86。", 0.86, 3, 980),
            "batch_lifetime": ("同批次 3 台设备进入中高风险队列，12 个月最高风险 31%。", 0.82, 1, 760),
            "fmea": ("高 RPN 项集中在绕组绝缘、引线连接点和套管密封。", 0.84, 2, 690),
            "decision": ("建议 24 小时内复核 DGA，安排带电检测并预生成重要工单。", 0.88, 4, 810),
            "review": ("事实性、完整性、合规性通过；2 条不确定性已标注。", 0.9, len(evidence), 540),
        }
        summary, confidence, evidence_count, duration_ms = results[agent_id]
        return {"summary": summary, "confidence": confidence, "evidence_count": evidence_count, "duration_ms": duration_ms}

    def _build_report(self, task: dict[str, Any], evidence: list[dict[str, Any]]) -> dict[str, Any]:
        equipment = store.get_equipment(task["input"]["equipment_id"]) or store.get_equipment("EQ-TR-001")
        batch_risks = store.batch_items if equipment and equipment["type"] == "Transformer" else []
        return {
            "report_id": f"rpt_{uuid4().hex[:8]}",
            "diagnosis_id": task["diagnosis_id"],
            "equipment_id": equipment["equipment_id"],
            "title": f"{equipment['name']} Hermes Agent 白盒诊断报告",
            "risk_level": task["input"].get("priority", "important"),
            "root_causes": [
                {"name": "绕组引线连接点局部放电", "confidence": 0.86, "evidence_ids": ["EVR-001", "EVR-002", "EVR-003"]},
                {"name": "绝缘纸板局部劣化", "confidence": 0.72, "evidence_ids": ["EVR-001", "EVR-003"]},
                {"name": "高负荷导致局部过热", "confidence": 0.61, "evidence_ids": ["EVR-004"]},
            ],
            "component_path": ["变压器", "绕组", "引线连接点", "绝缘纸板"],
            "batch_risks": batch_risks,
            "fmea": [
                {"failure_mode": "绕组绝缘劣化", "component": "绕组/绝缘纸板", "severity": 9, "occurrence": 6, "detection": 5, "rpn": 270, "recommendation": "优先开展绝缘电阻与局放复测"},
                {"failure_mode": "引线连接点放电", "component": "引线连接点", "severity": 8, "occurrence": 5, "detection": 6, "rpn": 240, "recommendation": "安排红外与超声局放联合检测"},
                {"failure_mode": "油温异常升高", "component": "冷却系统", "severity": 7, "occurrence": 5, "detection": 4, "rpn": 140, "recommendation": "核查负荷与冷却器运行状态"},
            ],
            "work_order": {
                "title": f"{equipment['name']} DGA 异常复核与带电检测",
                "priority": task["input"].get("priority", "important"),
                "actions": ["复核 DGA 采样并缩短监测周期", "安排红外测温与超声局放检测", "查询同批次设备近 30 日趋势", "必要时申请计划停电检查绕组引线连接点"],
                "required_roles": ["变电检修工程师", "油化试验工程师", "运维值班负责人"],
                "spare_parts": ["绝缘材料备件", "油样采集耗材", "局放检测附件"],
                "safety_notes": ["带电检测保持安全距离", "油样复核需双人确认标签", "停电检查前完成风险预控票"],
                "estimated_hours": 6.5,
            },
            "review_findings": [
                {"level": "pass", "title": "证据链完整", "detail": "根因、批次、FMEA 与处置建议均绑定 evidence_id。"},
                {"level": "notice", "title": "存在不确定性", "detail": "缺少最近一次绝缘电阻试验数据，建议人工补充确认。"},
            ],
            "evidence_ids": [item["evidence_id"] for item in evidence],
            "created_at": datetime.now(),
        }
