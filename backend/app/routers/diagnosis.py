"""故障诊断路由"""
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from app.models.common import ApiResponse
from app.models.diagnosis import DiagnosisTriggerRequest, DiagnosisTriggerResponse, DiagnosisReport
from app.services.diagnosis_service import DiagnosisService

router = APIRouter()
ws_router = APIRouter()

_diagnosis_service = DiagnosisService()


def get_diagnosis_service() -> DiagnosisService:
    return _diagnosis_service


@router.post("/trigger", response_model=ApiResponse[DiagnosisTriggerResponse])
async def trigger_diagnosis(
    request: DiagnosisTriggerRequest,
    service: DiagnosisService = Depends(get_diagnosis_service),
):
    """触发故障诊断"""
    result = await service.trigger_diagnosis(request)
    return ApiResponse(data=result)


@router.get("/{diagnosis_id}", response_model=ApiResponse[DiagnosisReport | None])
async def get_diagnosis(
    diagnosis_id: str,
    service: DiagnosisService = Depends(get_diagnosis_service),
):
    """获取诊断结果"""
    result = await service.get_diagnosis(diagnosis_id)
    if result is None:
        return ApiResponse(code=404, message=f"诊断任务 {diagnosis_id} 不存在", data=None)
    return ApiResponse(data=result)


@ws_router.websocket("/ws/diagnosis/{diagnosis_id}")
async def diagnosis_progress_ws(websocket: WebSocket, diagnosis_id: str):
    """WebSocket 实时推送诊断进度"""
    await websocket.accept()

    service = get_diagnosis_service()

    try:
        # 先发送连接成功消息
        await websocket.send_json({
            "event_type": "connected",
            "diagnosis_id": diagnosis_id,
            "message": "WebSocket连接已建立，诊断进度推送开始",
        })

        # 推送诊断进度
        async for event in service.get_diagnosis_progress(diagnosis_id):
            await websocket.send_text(event)

        # 发送最终完成消息
        await websocket.send_json({
            "event_type": "stream_end",
            "message": "所有诊断进度推送完毕",
        })

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({
                "event_type": "error",
                "message": f"诊断进度推送异常: {str(e)}",
            })
        except Exception:
            pass
    finally:
        try:
            await websocket.close()
        except Exception:
            pass
