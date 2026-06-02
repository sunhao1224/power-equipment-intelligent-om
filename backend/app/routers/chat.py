"""运维问答路由"""
from fastapi import APIRouter, Depends

from app.models.common import ApiResponse
from app.models.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter()

# 服务实例（依赖注入）
_chat_service = ChatService()


def get_chat_service() -> ChatService:
    return _chat_service


@router.post("", response_model=ApiResponse[ChatResponse])
async def chat(
    request: ChatRequest,
    service: ChatService = Depends(get_chat_service),
):
    """发送消息，获取AI回答"""
    result = await service.chat(request)
    return ApiResponse(data=result)
