"""ExceptionHandler模块：统一接管系统异常处理（支持开发/生产环境）。"""

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import (
    RequestValidationError,
    HTTPException as FastAPIHTTPException,
)
from fastboot.logger import Logger
import traceback
import os


class ExceptionHandler:
    """统一异常处理器，用于捕获并格式化系统错误。"""

    def __init__(self, app):
        """初始化并注册异常处理器。

        Args:
            app (FastAPI): FastAPI应用实例。
        """
        self.app = app
        self.logger = Logger()
        self.is_dev = os.getenv("FASTBOOT_ENV", "dev") == "dev"  # 根据环境变量判断
        self.register_handlers()

    def register_handlers(self):
        """注册所有需要捕获的异常类型。"""
        self.app.add_exception_handler(
            FastAPIHTTPException, self.http_exception_handler
        )
        self.app.add_exception_handler(
            RequestValidationError, self.validation_exception_handler
        )
        self.app.add_exception_handler(Exception, self.global_exception_handler)

    async def http_exception_handler(self, request: Request, exc: FastAPIHTTPException):
        """处理FastAPI内置HTTP异常。"""
        self.logger.warning(
            f"[HTTPException] {request.method} {request.url}: {exc.detail}"
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "data": None,
                "error": str(exc.detail),
            },
        )

    async def validation_exception_handler(
        self, request: Request, exc: RequestValidationError
    ):
        """处理请求参数校验异常。"""
        self.logger.warning(
            f"[ValidationError] {request.method} {request.url}: {exc.errors()}"
        )
        return JSONResponse(
            status_code=422,
            content={"success": False, "data": None, "error": str(exc.errors())},
        )

    async def global_exception_handler(self, request: Request, exc: Exception):
        """处理所有未捕获的其他异常。"""
        self.logger.error(f"[Exception] {request.method} {request.url}: {str(exc)}")
        if self.is_dev:
            error_detail = {
                "type": exc.__class__.__name__,
                "message": str(exc),
                "traceback": traceback.format_exc(),
            }
        else:
            error_detail = "系统内部错误，请联系管理员"

        return JSONResponse(
            status_code=500,
            content={"success": False, "data": None, "error": error_detail},
        )
