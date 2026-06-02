"""故障诊断模型"""
from typing import Optional, Any
from pydantic import BaseModel, Field


class SensorDataInput(BaseModel):
    """传感器数据输入"""
    sensor_type: str = Field(..., description="传感器类型")
    value: float = Field(..., description="当前值")
    unit: str = Field(default="", description="单位")
    threshold: Optional[float] = Field(default=None, description="阈值")


class DiagnosisTriggerRequest(BaseModel):
    """触发诊断请求"""
    equipment_id: str = Field(..., description="设备ID")
    event_type: str = Field(..., description="事件类型", examples=["dga_alarm", "temperature_alarm", "pd_alarm"])
    sensor_data: list[SensorDataInput] = Field(default_factory=list, description="传感器数据")


class DiagnosisTriggerResponse(BaseModel):
    """触发诊断响应"""
    diagnosis_id: str = Field(..., description="诊断任务ID")
    status: str = Field(default="processing", description="状态")


class EvidenceItem(BaseModel):
    """证据项"""
    step: int = Field(..., description="步骤序号")
    evidence: str = Field(..., description="证据描述")
    confidence: float = Field(..., description="置信度", ge=0, le=1)


class RootCauseAnalysis(BaseModel):
    """根因分析"""
    conclusion: str = Field(..., description="根因结论")
    evidence_chain: list[EvidenceItem] = Field(default_factory=list, description="证据链")
    confidence: float = Field(..., description="综合置信度", ge=0, le=1)


class BatchRisk(BaseModel):
    """批次风险"""
    batch_id: str = Field(..., description="批次标识")
    risk_level: str = Field(..., description="风险等级")
    affected_devices: list[str] = Field(default_factory=list, description="受影响设备")
    recommendation: str = Field(default="", description="建议")


class CorrectiveAction(BaseModel):
    """处置建议"""
    priority: int = Field(..., description="优先级")
    action: str = Field(..., description="建议措施")
    timeframe: str = Field(default="", description="时间要求")


class EquipmentInfo(BaseModel):
    """设备信息"""
    equipment_id: str
    name: str
    type: str
    model: str
    manufacturer: str
    voltage_level: str
    substation: str


class DiagnosisReport(BaseModel):
    """诊断报告"""
    diagnosis_id: str = Field(..., description="诊断ID")
    status: str = Field(default="completed", description="状态")
    equipment: Optional[EquipmentInfo] = Field(default=None, description="设备信息")
    fault_symptom: str = Field(default="", description="故障现象")
    data_analysis: dict = Field(default_factory=dict, description="数据分析")
    root_cause: Optional[RootCauseAnalysis] = Field(default=None, description="根因分析")
    batch_risk: Optional[BatchRisk] = Field(default=None, description="批次风险")
    corrective_actions: list[CorrectiveAction] = Field(default_factory=list, description="处置建议")
    reasoning_trace: list[dict] = Field(default_factory=list, description="推理过程追溯")
    created_at: str = Field(default="", description="创建时间")
    completed_at: str = Field(default="", description="完成时间")
