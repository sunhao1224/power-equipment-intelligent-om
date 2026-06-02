"""批次评估模型"""
from typing import Optional
from pydantic import BaseModel, Field


class BatchAssessRequest(BaseModel):
    """批次评估请求"""
    equipment_id: str = Field(..., description="触发设备ID")
    batch_criteria: dict = Field(
        default_factory=lambda: {"manufacturer": True, "model": True, "year": True},
        description="批次匹配条件",
    )


class RiskDevice(BaseModel):
    """风险设备"""
    equipment_id: str
    name: str
    health_index: float
    risk_level: str
    risk_score: float
    issue_description: str


class BatchReport(BaseModel):
    """批次报告"""
    batch_description: str = Field(..., description="批次描述")
    total_count: int = Field(..., description="批次设备总数")
    risk_summary: dict = Field(default_factory=dict, description="风险汇总")
    statistical_analysis: dict = Field(default_factory=dict, description="统计分析")
    recommendations: list[str] = Field(default_factory=list, description="建议措施")
    risk_level: str = Field(default="低", description="批次风险等级")


class BatchAssessResponse(BaseModel):
    """批次评估响应"""
    batch_size: int = Field(..., description="批次规模")
    risk_devices: list[RiskDevice] = Field(default_factory=list, description="风险设备列表")
    batch_report: BatchReport = Field(..., description="批次报告")
