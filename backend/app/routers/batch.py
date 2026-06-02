"""批次评估路由"""
from fastapi import APIRouter, Depends

from app.models.common import ApiResponse
from app.models.batch import BatchAssessRequest, BatchAssessResponse
from app.services.batch_service import BatchService

router = APIRouter()

_batch_service = BatchService()


def get_batch_service() -> BatchService:
    return _batch_service


@router.post("/assess", response_model=ApiResponse[BatchAssessResponse])
async def batch_assess(
    request: BatchAssessRequest,
    service: BatchService = Depends(get_batch_service),
):
    """触发批次评估"""
    result = await service.assess(request)
    return ApiResponse(data=result)
