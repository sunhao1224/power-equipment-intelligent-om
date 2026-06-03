"""FastAPI entry for the redesigned Hermes Agent service."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.routers.hermes import api_router, ws_router

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Hermes Agent 驱动的电力设备智能运维分析与决策支持系统 API",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class BizException(Exception):
    def __init__(self, code: int = 400, message: str = "业务错误"):
        self.code = code
        self.message = message


@app.exception_handler(BizException)
async def biz_exception_handler(request: Request, exc: BizException):
    return JSONResponse(status_code=400, content={"code": exc.code, "message": exc.message, "data": None})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"code": 422, "message": f"参数校验失败: {exc.errors()}", "data": None})


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"code": 500, "message": f"服务器内部错误: {str(exc)}", "data": None})


app.include_router(api_router, prefix=settings.api_prefix, tags=["Hermes Agent"])
app.include_router(ws_router, tags=["Hermes Agent WebSocket"])


@app.get("/")
async def root():
    return {
        "code": 0,
        "message": "欢迎使用 Hermes Agent 电力设备智能运维系统",
        "data": {"version": settings.app_version, "docs": "/docs"},
    }


@app.get("/health")
async def health_check():
    return {"code": 0, "message": "ok", "data": {"status": "healthy", "version": settings.app_version}}
