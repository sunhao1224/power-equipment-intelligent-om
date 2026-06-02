"""知识管理路由"""
from fastapi import APIRouter, Depends

from app.models.common import ApiResponse
from app.models.knowledge import (
    KnowledgeUploadRequest,
    KnowledgeSearchRequest,
    KnowledgeSearchResponse,
)
from app.services.knowledge_service import KnowledgeService

router = APIRouter()

_knowledge_service = KnowledgeService()


def get_knowledge_service() -> KnowledgeService:
    return _knowledge_service


@router.post("/upload")
async def upload_knowledge(
    request: KnowledgeUploadRequest,
    service: KnowledgeService = Depends(get_knowledge_service),
):
    """上传知识文档"""
    result = await service.upload(request)
    return ApiResponse(data=result)


@router.get("/search", response_model=ApiResponse[KnowledgeSearchResponse])
async def search_knowledge(
    query: str,
    top_k: int = 5,
    domain: str | None = None,
    service: KnowledgeService = Depends(get_knowledge_service),
):
    """语义检索知识"""
    request = KnowledgeSearchRequest(query=query, top_k=top_k, domain=domain)
    result = await service.search(request)
    return ApiResponse(data=result)
