"""故障诊断服务"""
import uuid
import json
import asyncio
from datetime import datetime
from typing import AsyncGenerator

from app.models.diagnosis import (
    DiagnosisTriggerRequest,
    DiagnosisTriggerResponse,
    DiagnosisReport,
    EvidenceItem,
    RootCauseAnalysis,
    BatchRisk,
    CorrectiveAction,
    EquipmentInfo,
)
from app.mock_data.equipment import get_equipment_by_id, EQUIPMENT_LIST
from app.mock_data.sensors import get_dga_data, get_partial_discharge_data
from app.mock_data.faults import get_fault_case_by_equipment
from app.mock_data.knowledge import search_knowledge


# 内存存储诊断结果
_diagnosis_store: dict[str, DiagnosisReport] = {}


class DiagnosisService:
    """故障诊断服务"""

    async def trigger_diagnosis(self, request: DiagnosisTriggerRequest) -> DiagnosisTriggerResponse:
        """触发诊断"""
        diagnosis_id = f"DIAG-{uuid.uuid4().hex[:8].upper()}"

        # 异步生成诊断报告（模拟处理）
        report = await self._generate_diagnosis(diagnosis_id, request)
        _diagnosis_store[diagnosis_id] = report

        return DiagnosisTriggerResponse(
            diagnosis_id=diagnosis_id,
            status="processing",
        )

    async def get_diagnosis(self, diagnosis_id: str) -> DiagnosisReport | None:
        """获取诊断结果"""
        return _diagnosis_store.get(diagnosis_id)

    async def get_diagnosis_progress(self, diagnosis_id: str) -> AsyncGenerator[str, None]:
        """WebSocket 实时推送诊断进度"""
        agents = [
            {
                "event_type": "agent_start",
                "agent_name": "数据采集Agent",
                "agent_id": "data_collection",
                "description": "采集设备多维传感器数据",
            },
            {
                "event_type": "agent_progress",
                "agent_name": "数据采集Agent",
                "agent_id": "data_collection",
                "progress": 50,
                "detail": "正在获取DGA数据和温度数据...",
            },
            {
                "event_type": "agent_complete",
                "agent_name": "数据采集Agent",
                "agent_id": "data_collection",
                "result": "已成功采集DGA、油温、绕组温度、局放等4类传感器数据",
            },
            {
                "event_type": "agent_start",
                "agent_name": "特征分析Agent",
                "agent_id": "feature_analysis",
                "description": "对采集数据进行特征提取和异常检测",
            },
            {
                "event_type": "agent_progress",
                "agent_name": "特征分析Agent",
                "agent_id": "feature_analysis",
                "progress": 60,
                "detail": "正在进行DGA三比值法计算和趋势分析...",
            },
            {
                "event_type": "agent_complete",
                "agent_name": "特征分析Agent",
                "agent_id": "feature_analysis",
                "result": "检测到3项异常特征：总烃超标、C2H2检出、温度上升趋势",
            },
            {
                "event_type": "agent_start",
                "agent_name": "知识推理Agent",
                "agent_id": "knowledge_reasoning",
                "description": "结合知识库进行故障推理",
            },
            {
                "event_type": "agent_progress",
                "agent_name": "知识推理Agent",
                "agent_id": "knowledge_reasoning",
                "progress": 70,
                "detail": "检索到5条相关知识，正在进行故障模式匹配...",
            },
            {
                "event_type": "agent_complete",
                "agent_name": "知识推理Agent",
                "agent_id": "knowledge_reasoning",
                "result": "匹配故障模式：高温过热故障，置信度0.89",
            },
            {
                "event_type": "agent_start",
                "agent_name": "批次评估Agent",
                "agent_id": "batch_assessment",
                "description": "评估同批次设备风险",
            },
            {
                "event_type": "agent_complete",
                "agent_name": "批次评估Agent",
                "agent_id": "batch_assessment",
                "result": "同批次3台设备中，1台存在类似风险",
            },
            {
                "event_type": "agent_start",
                "agent_name": "决策建议Agent",
                "agent_id": "decision_advisor",
                "description": "生成处置建议和维护方案",
            },
            {
                "event_type": "agent_complete",
                "agent_name": "决策建议Agent",
                "agent_id": "decision_advisor",
                "result": "已生成4条处置建议和3条预防措施",
            },
            {
                "event_type": "diagnosis_done",
                "diagnosis_id": diagnosis_id,
                "summary": "诊断完成：判定为高温过热故障，建议尽快安排停电检修",
            },
            {
                "event_type": "review_result",
                "review_status": "pending",
                "reviewer": "待分配",
                "note": "诊断报告已生成，等待专家审核确认",
            },
        ]

        for agent_event in agents:
            await asyncio.sleep(1.2 + (hash(str(agent_event)) % 800) / 1000)
            yield json.dumps(agent_event, ensure_ascii=False)

    async def _generate_diagnosis(self, diagnosis_id: str, request: DiagnosisTriggerRequest) -> DiagnosisReport:
        """生成完整诊断报告"""
        eq = get_equipment_by_id(request.equipment_id)
        now = datetime.now()

        # 设备信息
        equipment_info = None
        if eq:
            equipment_info = EquipmentInfo(
                equipment_id=eq["equipment_id"],
                name=eq["name"],
                type=eq["type_name"],
                model=eq["model"],
                manufacturer=eq["manufacturer"],
                voltage_level=eq["voltage_level"],
                substation=eq["substation"],
            )

        # 数据分析
        data_analysis = {}
        if eq and eq["type"] == "transformer":
            dga = get_dga_data(request.equipment_id)
            data_analysis["dga"] = {
                "latest_sample": dga["latest"],
                "diagnosis": dga["diagnosis"],
                "thresholds": dga["attention_thresholds"],
            }
            pd_data = get_partial_discharge_data(request.equipment_id)
            data_analysis["partial_discharge"] = pd_data["summary"]

        # 传感器输入
        sensor_summary = {}
        for sd in request.sensor_data:
            sensor_summary[sd.sensor_type] = {
                "value": sd.value,
                "unit": sd.unit,
                "threshold": sd.threshold,
                "status": "超标" if sd.threshold and sd.value > sd.threshold else "正常",
            }
        data_analysis["sensor_data"] = sensor_summary

        # 根据事件类型生成不同的诊断结果
        event_type = request.event_type
        root_cause = self._generate_root_cause(event_type, eq)
        fault_symptom = self._generate_fault_symptom(event_type, request, eq)
        batch_risk = self._generate_batch_risk(event_type, eq)
        corrective_actions = self._generate_corrective_actions(event_type)

        # 推理过程追溯
        reasoning_trace = [
            {"step": 1, "action": "数据采集", "input": f"设备 {request.equipment_id} 的传感器数据",
             "output": f"采集到 {len(request.sensor_data)} 项传感器数据", "agent": "数据采集Agent"},
            {"step": 2, "action": "特征提取", "input": "原始传感器数据",
             "output": "提取到异常特征：温度上升、DGA超标", "agent": "特征分析Agent"},
            {"step": 3, "action": "知识检索", "input": "异常特征描述",
             "output": "匹配到3条相关知识条目", "agent": "知识推理Agent"},
            {"step": 4, "action": "故障推理", "input": "异常特征 + 知识库",
             "output": root_cause["conclusion"], "agent": "知识推理Agent"},
            {"step": 5, "action": "批次评估", "input": f"设备 {request.equipment_id} 的厂家型号信息",
             "output": f"同批次 {batch_risk['total_count']} 台设备", "agent": "批次评估Agent"},
            {"step": 6, "action": "建议生成", "input": "诊断结论 + 设备状态",
             "output": f"生成 {len(corrective_actions)} 条处置建议", "agent": "决策建议Agent"},
        ]

        return DiagnosisReport(
            diagnosis_id=diagnosis_id,
            status="completed",
            equipment=equipment_info,
            fault_symptom=fault_symptom,
            data_analysis=data_analysis,
            root_cause=RootCauseAnalysis(**root_cause),
            batch_risk=BatchRisk(**batch_risk) if batch_risk else None,
            corrective_actions=[CorrectiveAction(**a) for a in corrective_actions],
            reasoning_trace=reasoning_trace,
            created_at=now.isoformat(),
            completed_at=now.isoformat(),
        )

    def _generate_root_cause(self, event_type: str, eq: dict | None) -> dict:
        """生成根因分析"""
        causes = {
            "dga_alarm": {
                "conclusion": "变压器内部存在高温过热故障，DGA三比值法分析诊断为T2型过热（温度>700°C），"
                              "结合温度上升趋势，初步判断为绕组匝间绝缘劣化导致的局部过热。",
                "evidence_chain": [
                    {"step": 1, "evidence": "DGA数据：总烃超过150ppm注意值，C2H2检出", "confidence": 0.95},
                    {"step": 2, "evidence": "三比值法判断为高温过热故障类型", "confidence": 0.92},
                    {"step": 3, "evidence": "油温30天趋势上升3-5°C", "confidence": 0.88},
                    {"step": 4, "evidence": "绕组直流电阻不平衡率接近注意值", "confidence": 0.85},
                    {"step": 5, "evidence": "铁芯接地电流有轻微增大", "confidence": 0.78},
                ],
                "confidence": 0.89,
            },
            "temperature_alarm": {
                "conclusion": "变压器油温异常升高，综合分析冷却系统正常、负荷未超限，"
                              "DGA检测发现特征气体增长，判断为内部故障导致的温度升高。",
                "evidence_chain": [
                    {"step": 1, "evidence": "油温持续升高超过85°C注意值", "confidence": 0.97},
                    {"step": 2, "evidence": "负荷电流在正常范围内", "confidence": 0.90},
                    {"step": 3, "evidence": "冷却系统运行正常", "confidence": 0.88},
                    {"step": 4, "evidence": "DGA检测发现CH4和C2H4增长", "confidence": 0.85},
                ],
                "confidence": 0.85,
            },
            "pd_alarm": {
                "conclusion": "设备检测到异常局部放电信号，PRPD谱图特征分析显示为自由颗粒放电模式，"
                              "可能由金属微粒或绝缘缺陷引起。",
                "evidence_chain": [
                    {"step": 1, "evidence": "UHF局放信号幅值超过300mV", "confidence": 0.96},
                    {"step": 2, "evidence": "PRPD谱图呈现自由颗粒放电特征", "confidence": 0.91},
                    {"step": 3, "evidence": "超声波检测辅助确认异常信号", "confidence": 0.87},
                    {"step": 4, "evidence": "信号幅值有增大趋势", "confidence": 0.83},
                ],
                "confidence": 0.88,
            },
        }
        return causes.get(event_type, causes["dga_alarm"])

    def _generate_fault_symptom(self, event_type: str, request: DiagnosisTriggerRequest, eq: dict | None) -> str:
        """生成故障现象描述"""
        eq_name = eq["name"] if eq else "未知设备"
        sensor_desc = ""
        if request.sensor_data:
            parts = []
            for sd in request.sensor_data:
                parts.append(f"{sd.sensor_type}={sd.value}{sd.unit}")
            sensor_desc = "，".join(parts)

        symptom_map = {
            "dga_alarm": f"{eq_name} DGA在线监测发现油中溶解气体异常，{sensor_desc or '总烃超过注意值'}。"
                         f"近30天DGA数据显示特征气体持续增长，C2H2含量检出，需高度关注。",
            "temperature_alarm": f"{eq_name} 油温监测发现异常升高，{sensor_desc or '油温超过85°C注意值'}。"
                                 f"近7天温度呈持续上升趋势，与环境温度和负荷变化不匹配。",
            "pd_alarm": f"{eq_name} 局部放电在线监测发现异常信号，{sensor_desc or 'UHF信号幅值超过300mV'}。"
                        f"PRPD谱图分析显示放电活动主要集中在工频正半周和负半周的峰值附近。",
        }
        return symptom_map.get(event_type, symptom_map["dga_alarm"])

    def _generate_batch_risk(self, event_type: str, eq: dict | None) -> dict | None:
        """生成批次风险评估"""
        if not eq:
            return None

        # 查找同厂家同型号设备
        same_batch = [
            e for e in EQUIPMENT_LIST
            if e["manufacturer"] == eq["manufacturer"]
            and e["type"] == eq["type"]
            and e["equipment_id"] != eq["equipment_id"]
        ]

        risk_devices = [e["equipment_id"] for e in same_batch if e["health_index"] < 80]

        return {
            "batch_id": f"BATCH-{eq['manufacturer']}-{eq['model'][:10]}",
            "risk_level": "中" if risk_devices else "低",
            "affected_devices": risk_devices,
            "recommendation": f"同批次共{len(same_batch)}台设备，其中{len(risk_devices)}台健康指数偏低，"
                              f"建议对同批次设备开展专项检查。" if risk_devices
                              else f"同批次共{len(same_batch)}台设备，目前状态整体良好。",
            "total_count": len(same_batch) + 1,
        }

    def _generate_corrective_actions(self, event_type: str) -> list[dict]:
        """生成处置建议"""
        actions_map = {
            "dga_alarm": [
                {"priority": 1, "action": "立即降低负荷至额定60%，减缓故障发展", "timeframe": "立即执行"},
                {"priority": 2, "action": "安排DGA复测，确认数据准确性并计算产气速率", "timeframe": "24小时内"},
                {"priority": 3, "action": "开展绕组直流电阻和短路阻抗测试", "timeframe": "3天内"},
                {"priority": 4, "action": "根据试验结果评估是否需要停电检修", "timeframe": "1周内"},
            ],
            "temperature_alarm": [
                {"priority": 1, "action": "检查冷却系统运行状态，确保全部冷却器投入", "timeframe": "立即执行"},
                {"priority": 2, "action": "降低负荷至额定70%以下", "timeframe": "立即执行"},
                {"priority": 3, "action": "进行DGA快速检测，排除内部故障可能", "timeframe": "12小时内"},
                {"priority": 4, "action": "若温度不降或DGA异常，申请停电检查", "timeframe": "24小时内"},
            ],
            "pd_alarm": [
                {"priority": 1, "action": "增加局放检测频次，持续监测PRPD谱图变化", "timeframe": "立即执行"},
                {"priority": 2, "action": "采用超声波检测进行缺陷定位", "timeframe": "48小时内"},
                {"priority": 3, "action": "评估缺陷严重程度，制定停电处理方案", "timeframe": "1周内"},
                {"priority": 4, "action": "安排停电处理并进行耐压试验验证", "timeframe": "2周内"},
            ],
        }
        return actions_map.get(event_type, actions_map["dga_alarm"])
