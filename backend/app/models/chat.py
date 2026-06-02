"""运维问答模型"""
from typing import Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """聊天请求"""
    message: str = Field(..., description="用户消息", min_length=1, max_length=2000)
    conversation_id: str = Field(default="default", description="会话ID")
    equipment_id: Optional[str] = Field(default=None, description="关联设备ID")


class Reference(BaseModel):
    """引用知识"""
    title: str = Field(..., description="文档标题")
    source: str = Field(..., description="来源")
    relevance: float = Field(..., description="相关度", ge=0, le=1)


class ChatResponse(BaseModel):
    """聊天响应"""
    answer: str = Field(..., description="AI回答")
    references: list[Reference] = Field(default_factory=list, description="引用知识列表")
    confidence: float = Field(..., description="置信度", ge=0, le=1)
    conversation_id: str = Field(..., description="会话ID")
