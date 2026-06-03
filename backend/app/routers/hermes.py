"""REST and WebSocket endpoints for the redesigned Hermes Agent demo."""

from __future__ import annotations

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from fastapi.encoders import jsonable_encoder

from app.agent_runtime import ChiefDiagnosisOrchestrator
from app.repositories.mock import store
from app.schemas import ApiResponse, BatchAssessmentRequest, DiagnosisInput

api_router = APIRouter()
ws_router = APIRouter()
orchestrator = ChiefDiagnosisOrchestrator()


def ok(data=None, message: str = "ok") -> ApiResponse:
    return ApiResponse(code=0, message=message, data=data)


@api_router.get("/overview", response_model=ApiResponse)
async def overview():
    equipment = store.list_equipment()
    reports = store.list_reports()
    return ok({
        "metrics": [
            {"label": "在线设备", "value": len(equipment), "delta": "+12%", "tone": "primary"},
            {"label": "高风险设备", "value": len([e for e in equipment if e["risk_level"] in ("important", "critical")]), "delta": "-8%", "tone": "warning"},
            {"label": "Agent 会诊", "value": len(store.diagnoses), "delta": "+24%", "tone": "success"},
            {"label": "证据完整率", "value": "96.8%", "delta": "+3.1%", "tone": "success"},
        ],
        "health_trend": [
            {"day": "Mon", "score": 82}, {"day": "Tue", "score": 80}, {"day": "Wed", "score": 78},
            {"day": "Thu", "score": 76}, {"day": "Fri", "score": 74}, {"day": "Sat", "score": 73}, {"day": "Sun", "score": 72},
        ],
        "risk_equipment": equipment,
        "recent_reports": reports[:5],
        "agent_stats": [
            {"name": "Data Sensing", "avg_ms": 620}, {"name": "RAG", "avg_ms": 740}, {"name": "RCA", "avg_ms": 980},
            {"name": "Batch", "avg_ms": 760}, {"name": "FMEA", "avg_ms": 690}, {"name": "Review", "avg_ms": 540},
        ],
    })


@api_router.get("/equipment", response_model=ApiResponse)
async def list_equipment():
    return ok(store.list_equipment())


@api_router.get("/equipment/{equipment_id}", response_model=ApiResponse)
async def get_equipment(equipment_id: str):
    item = store.get_equipment(equipment_id)
    return ok(item, "equipment found" if item else "equipment not found")


@api_router.get("/events/mock", response_model=ApiResponse)
async def list_events():
    return ok(store.list_events())


@api_router.post("/diagnosis/trigger", response_model=ApiResponse)
async def trigger_diagnosis(payload: DiagnosisInput):
    data = payload.model_dump()
    if payload.event_type == "mock_event":
        event = store.get_event(payload.event_id)
        if event:
            data["equipment_id"] = event["equipment_id"]
            data["sensor_data"] = event["sensor_data"]
            data["time_window"] = event["time_window"]
            data["priority"] = event["priority"]
            data["event_title"] = event["title"]
            data["event_summary"] = event["summary"]
    task = store.create_diagnosis(data)
    return ok({
        "diagnosis_id": task["diagnosis_id"],
        "orchestrator_id": task["orchestrator_id"],
        "agent_trace_id": task["agent_trace_id"],
        "status": task["status"],
    }, "diagnosis created")


@api_router.get("/diagnosis/{diagnosis_id}", response_model=ApiResponse)
async def get_diagnosis(diagnosis_id: str):
    return ok(store.get_task(diagnosis_id))


@api_router.get("/agents/traces/{trace_id}", response_model=ApiResponse)
async def get_trace(trace_id: str):
    return ok(store.get_trace(trace_id))


@api_router.get("/knowledge/evidence", response_model=ApiResponse)
async def list_evidence(q: str | None = Query(default=None)):
    return ok({
        "items": store.list_evidence(q),
        "graph": {
            "nodes": ["Transformer", "DGA", "C2H2", "ArcDischarge", "Winding", "LeadConnection", "Batch"],
            "edges": [
                ["Transformer", "DGA"], ["DGA", "C2H2"], ["C2H2", "ArcDischarge"],
                ["Transformer", "Winding"], ["Winding", "LeadConnection"], ["Transformer", "Batch"],
            ],
        },
    })


@api_router.post("/batch/assess", response_model=ApiResponse)
async def assess_batch(payload: BatchAssessmentRequest):
    return ok({
        "equipment_id": payload.equipment_id,
        "items": store.batch_items,
        "summary": "同批次设备存在聚集性 DGA 与温升趋势异常，建议纳入专项监测。",
    })


@api_router.get("/reports", response_model=ApiResponse)
async def list_reports():
    return ok(store.list_reports())


@api_router.get("/reports/{report_id}", response_model=ApiResponse)
async def get_report(report_id: str):
    return ok(store.get_report(report_id))


@ws_router.websocket("/ws/diagnosis/{diagnosis_id}")
async def diagnosis_ws(websocket: WebSocket, diagnosis_id: str):
    await websocket.accept()
    try:
        async for event in orchestrator.stream(diagnosis_id):
            await websocket.send_json(jsonable_encoder(event))
    except WebSocketDisconnect:
        return
    finally:
        await websocket.close()
