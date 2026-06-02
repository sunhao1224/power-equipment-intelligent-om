"""FastAPI 入口"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.config import get_settings
from app.routers import chat, diagnosis, batch, maintenance, knowledge, equipment

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="基于大语言模型的电力设备智能运维分析与决策支持系统 API",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== 全局异常处理 ====================

class BizException(Exception):
    """业务异常"""
    def __init__(self, code: int = 400, message: str = "业务错误"):
        self.code = code
        self.message = message


@app.exception_handler(BizException)
async def biz_exception_handler(request: Request, exc: BizException):
    return JSONResponse(
        status_code=200,
        content={"code": exc.code, "message": exc.message, "data": None},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=200,
        content={"code": 422, "message": f"参数校验失败: {exc.errors()}", "data": None},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=200,
        content={"code": 500, "message": f"服务器内部错误: {str(exc)}", "data": None},
    )


# ==================== 注册路由 ====================

app.include_router(chat.router, prefix=f"{settings.api_prefix}/chat", tags=["运维问答"])
app.include_router(diagnosis.router, prefix=f"{settings.api_prefix}/diagnosis", tags=["故障诊断"])
app.include_router(batch.router, prefix=f"{settings.api_prefix}/batch", tags=["批次评估"])
app.include_router(maintenance.router, prefix=f"{settings.api_prefix}/maintenance", tags=["维护决策"])
app.include_router(knowledge.router, prefix=f"{settings.api_prefix}/knowledge", tags=["知识管理"])
app.include_router(equipment.router, prefix=f"{settings.api_prefix}/equipment", tags=["设备管理"])

# WebSocket 路由单独注册（不带 /api/v1 前缀）
app.include_router(diagnosis.ws_router, tags=["故障诊断-WebSocket"])


# ==================== 根路由 ====================

@app.get("/")
async def root():
    return {
        "code": 0,
        "message": "欢迎使用电力设备智能运维分析与决策支持系统",
        "data": {"version": settings.app_version, "docs": "/docs"},
    }


@app.get("/health")
async def health_check():
    return {"code": 0, "message": "ok", "data": {"status": "healthy"}}
