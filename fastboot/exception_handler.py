# fastboot/exception_handler.py
"""ExceptionHandler模块：统一接管系统异常处理。"""

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException
from fastboot.logger import Logger

class ExceptionHandler:
    """统一异常处理器，用于捕获并格式化系统错误。"""

    def __init__(self, app):
        """初始化并注册异常处理器。

        Args:
            app (FastAPI): FastAPI应用实例。
        """
        self.app = app
        self.logger = Logger()
        self.register_handlers()

    def register_handlers(self):
        """注册所有需要捕获的异常类型。"""
        self.app.add_exception_handler(HTTPException, self.http_exception_handler)
        self.app.add_exception_handler(RequestValidationError, self.validation_exception_handler)
        self.app.add_exception_handler(Exception, self.global_exception_handler)

    async def http_exception_handler(self, request: Request, exc: HTTPException):
        """处理FastAPI内置HTTP异常。"""
        self.logger.warning(f"HTTPException: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "type": "HTTPException",
                    "message": exc.detail,
                }
            }
        )

    async def validation_exception_handler(self, request: Request, exc: RequestValidationError):
        """处理请求参数校验异常。"""
        self.logger.warning(f"RequestValidationError: {exc.errors()}")
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": {
                    "type": "ValidationError",
                    "message": exc.errors(),
                }
            }
        )

    async def global_exception_handler(self, request: Request, exc: Exception):
        """处理所有未捕获的其他异常。"""
        self.logger.error(f"Unhandled Exception: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "type": exc.__class__.__name__,
                    "message": str(exc),
                }
            }
        )
