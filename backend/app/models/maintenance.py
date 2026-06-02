"""维护决策模型"""
from typing import Optional
from pydantic import BaseModel, Field


class MaintenancePlanRequest(BaseModel):
    """维护计划请求"""
    equipment_ids: list[str] = Field(..., description="设备ID列表", min_length=1)
    time_horizon: int = Field(default=90, description="计划周期（天）", ge=7, le=365)


class WorkOrder(BaseModel):
    """工单"""
    order_id: str = Field(..., description="工单ID")
    equipment_id: str = Field(..., description="设备ID")
    equipment_name: str = Field(..., description="设备名称")
    task_type: str = Field(..., description="任务类型")
    priority: int = Field(..., description="优先级", ge=1, le=5)
    planned_date: str = Field(..., description="计划日期")
    estimated_hours: int = Field(..., description="预计工时(小时)")
    description: str = Field(default="", description="描述")
    status: str = Field(default="planned", description="状态")


class MaintenancePlanItem(BaseModel):
    """维护计划项"""
    equipment_id: str
    equipment_name: str
    health_index: float
    plan_type: str = Field(..., description="计划类型")
    recommended_actions: list[str] = Field(default_factory=list, description="建议措施")
    planned_date: str = Field(default="", description="建议日期")
    urgency: str = Field(default="normal", description="紧急程度")


class MaintenancePlanResponse(BaseModel):
    """维护计划响应"""
    plans: list[MaintenancePlanItem] = Field(default_factory=list, description="维护计划列表")
    work_orders: list[WorkOrder] = Field(default_factory=list, description="工单列表")


class HealthIndicator(BaseModel):
    """健康指标"""
    name: str
    score: float
    weight: float
    status: str
    details: str


class TrendPoint(BaseModel):
    """趋势点"""
    date: str
    health_index: float


class HealthResponse(BaseModel):
    """健康评分响应"""
    equipment_id: str
    health_index: float = Field(..., description="健康指数", ge=0, le=100)
    assessment_date: str = Field(default="", description="评估日期")
    indicators: dict = Field(default_factory=dict, description="各维度指标")
    trend: list[TrendPoint] = Field(default_factory=list, description="历史趋势")
    assessment_result: str = Field(default="", description="评估等级")
    recommendation: str = Field(default="", description="维护建议")
