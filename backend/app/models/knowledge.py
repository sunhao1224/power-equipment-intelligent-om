"""知识管理模型"""
from typing import Optional
from pydantic import BaseModel, Field


class KnowledgeUploadRequest(BaseModel):
    """知识上传请求"""
    title: str = Field(..., description="文档标题")
    content: str = Field(..., description="文档内容", min_length=1)
    domain: str = Field(default="通用", description="领域")
    doc_type: str = Field(default="运维知识", description="文档类型")
    source: str = Field(default="用户上传", description="来源")
    keywords: list[str] = Field(default_factory=list, description="关键词")


class KnowledgeSearchRequest(BaseModel):
    """知识搜索请求"""
    query: str = Field(..., description="查询关键词", min_length=1)
    top_k: int = Field(default=5, description="返回数量", ge=1, le=20)
    domain: Optional[str] = Field(default=None, description="领域过滤")


class KnowledgeItem(BaseModel):
    """知识条目"""
    doc_id: str
    title: str
    domain: str
    type: str
    source: str
    content: str
    relevance: float


class KnowledgeSearchResponse(BaseModel):
    """知识搜索响应"""
    query: str
    total: int
    results: list[KnowledgeItem]
