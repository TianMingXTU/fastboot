# fastboot/exception_handler.py
"""ExceptionHandler模块：统一接管系统异常处理，使用优化后的响应和日志。"""

from fastapi import FastAPI, Request, status as http_status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError # FastAPI内置的校验异常
from fastapi import HTTPException as FastAPIHTTPException # FastAPI内置的HTTP异常

from pydantic import ValidationError as PydanticValidationError # Pydantic自身的校验异常

# 导入您优化后的响应和日志类
from fastboot.response import ErrorResponse 
from fastboot.logger import Logger
from typing import Optional, Any
import traceback # 用于获取堆栈跟踪信息
import os

# (可选) 定义自定义业务异常基类，如果您的应用需要更细致的业务异常分类
class BaseAppException(Exception):
    """自定义业务异常的基类。"""
    def __init__(self, 
                 message: str, 
                 status_code: int = http_status.HTTP_400_BAD_REQUEST, 
                 error_code: Optional[str] = None, 
                 data: Any = None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.data = data # 用于携带额外错误信息的上下文
        super().__init__(message)

class AppNotFoundException(BaseAppException):
    """当特定资源未找到时抛出的异常。"""
    def __init__(self, resource_name: str = "资源", identifier: Any = None, error_code: str = "RESOURCE_NOT_FOUND"):
        message = f"{resource_name} '{identifier if identifier else ''}' 未找到。"
        super().__init__(message, status_code=http_status.HTTP_404_NOT_FOUND, error_code=error_code)

class AppValidationException(BaseAppException):
    """当业务层面的数据校验失败时抛出的异常。"""
    def __init__(self, message: str = "业务校验失败", error_code: str = "BUSINESS_VALIDATION_ERROR", data: Any = None):
        super().__init__(message, status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY, error_code=error_code, data=data)


class ExceptionHandler:
    """
    统一异常处理器，用于捕获并格式化系统错误。
    它使用 ErrorResponse 来生成标准化的JSON错误响应。
    """

    def __init__(self, app: FastAPI, logger: Logger): # 接收FastAPI应用实例和Logger实例
        """
        初始化并注册异常处理器。
        :param app: FastAPI应用实例。
        :param logger: Logger实例，用于记录异常。
        """
        self.app = app
        self.logger = logger # 保存传入的logger实例
        # 从环境变量或配置中判断是否为开发环境，以决定错误详情的暴露程度
        # 假设 ConfigManager 已在 FastBootApp 中初始化并可访问，或者直接从env获取
        self.is_dev_env = os.getenv("FASTBOOT_ENV", "dev").lower() == "dev" 
        self._register_all_handlers() # 注册所有异常处理器

    def _register_all_handlers(self):
        """注册所有需要捕获的异常类型的处理器。"""
        self.app.add_exception_handler(BaseAppException, self._handle_custom_app_exception)
        self.app.add_exception_handler(FastAPIHTTPException, self._handle_fastapi_http_exception)
        self.app.add_exception_handler(RequestValidationError, self._handle_request_validation_error)
        self.app.add_exception_handler(PydanticValidationError, self._handle_pydantic_validation_error)
        # (可选) 添加对特定数据库异常（如Tortoise ORM）的处理
        # from tortoise.exceptions import DoesNotExist, IntegrityError
        # self.app.add_exception_handler(DoesNotExist, self._handle_tortoise_does_not_exist)
        # self.app.add_exception_handler(IntegrityError, self._handle_tortoise_integrity_error)
        self.app.add_exception_handler(Exception, self._handle_generic_exception) # 捕获所有其他未处理的Python异常
        self.logger.info("全局异常处理器已注册所有处理器。")

    async def _handle_custom_app_exception(self, request: Request, exc: BaseAppException) -> JSONResponse:
        """处理自定义的 BaseAppException 及其子类。"""
        self.logger.warning(
            f"自定义业务异常捕获: {exc.message} (请求: {request.method} {request.url.path}, "
            f"错误码: {exc.error_code}, 状态码: {exc.status_code})"
        )
        return ErrorResponse.create( # 使用 ErrorResponse.create 来构建响应
            message=exc.message, 
            error_code=exc.error_code, 
            http_code=exc.status_code,
            data=exc.data
        )

    async def _handle_fastapi_http_exception(self, request: Request, exc: FastAPIHTTPException) -> JSONResponse:
        """处理FastAPI内置的HTTPException。"""
        self.logger.warning(
            f"FastAPI HTTPException捕获: \"{exc.detail}\" (请求: {request.method} {request.url.path}, 状态码: {exc.status_code})"
        )
        # FastAPI 的 exc.detail 可以是字符串或字典等。我们需要适配它。
        error_message = str(exc.detail) if not isinstance(exc.detail, dict) else exc.detail.get("error", str(exc.detail))
        error_data = exc.detail if isinstance(exc.detail, dict) and "error" not in exc.detail else None

        return ErrorResponse.create(
            message=error_message,
            http_code=exc.status_code,
            data=error_data
            # error_code 可以尝试从 exc.headers 或其他地方获取，如果API设计了传递方式
        )

    async def _handle_request_validation_error(self, request: Request, exc: RequestValidationError) -> JSONResponse:
        """处理FastAPI的请求体验证错误 (通常是Pydantic模型校验失败)。"""
        error_details = exc.errors() # 获取详细的字段错误列表
        self.logger.warning(
            f"FastAPI请求体验证失败 (RequestValidationError): {len(error_details)} 个字段错误 "
            f"(请求: {request.method} {request.url.path}) - 详情: {error_details}"
        )
        # 将详细的Pydantic错误信息放入响应的data字段
        return ErrorResponse.unprocessable_entity(
            message="请求参数校验失败，请检查您的输入。",
            data={"validation_errors": error_details} 
        )

    async def _handle_pydantic_validation_error(self, request: Request, exc: PydanticValidationError) -> JSONResponse:
        """处理直接由Pydantic抛出的校验错误 (如果某些地方手动使用Pydantic校验)。"""
        error_details = exc.errors()
        self.logger.warning(
            f"Pydantic原生校验失败 (ValidationError): {len(error_details)} 个字段错误 "
            f"(请求: {request.method} {request.url.path}) - 详情: {error_details}"
        )
        return ErrorResponse.unprocessable_entity(
            message="数据校验失败。",
            data={"validation_errors": error_details}
        )

    # --- (可选) 特定数据库异常处理器示例 ---
    # async def _handle_tortoise_does_not_exist(self, request: Request, exc: DoesNotExist) -> JSONResponse:
    #     self.logger.warning(f"Tortoise ORM记录未找到: {exc} (请求: {request.method} {request.url.path})")
    #     return ErrorResponse.not_found(message=f"请求的资源未找到。({str(exc)})")

    # async def _handle_tortoise_integrity_error(self, request: Request, exc: IntegrityError) -> JSONResponse:
    #     self.logger.error(f"Tortoise ORM数据库完整性错误: {exc} (请求: {request.method} {request.url.path})", exc_info=True)
    #     # 避免直接暴露敏感的数据库错误信息给客户端
    #     return ErrorResponse.create(
    #         message="数据库操作失败，可能由于数据冲突或违反约束。", 
    #         error_code="DB_INTEGRITY_VIOLATION", 
    #         http_code=http_status.HTTP_409_CONFLICT 
    #     )
    # --- END 可选数据库异常处理器 ---

    async def _handle_generic_exception(self, request: Request, exc: Exception) -> JSONResponse:
        """处理所有其他未被特定处理器捕获的Python异常。"""
        # 对于未知异常，记录完整的堆栈跟踪至关重要
        stack_trace = traceback.format_exc() if self.is_dev_env else None #仅开发环境获取完整堆栈
        self.logger.error(
            f"未处理的全局异常: {exc.__class__.__name__}: {str(exc)} "
            f"(请求: {request.method} {request.url.path})\n详细堆栈 (如果is_dev_env=True):\n{stack_trace if stack_trace else '生产环境不展示堆栈'}",
            # exc_info=True # 通常在生产环境中，对于未知错误也应记录完整堆栈到日志文件
        )
        
        # 根据环境决定暴露给客户端的错误信息
        if self.is_dev_env:
            error_detail_message = f"发生意外错误: {exc.__class__.__name__} - {str(exc)}"
            error_data = {"type": exc.__class__.__name__, "traceback": stack_trace} if stack_trace else None
        else:
            error_detail_message = "服务器在处理您的请求时发生了一个意外错误。请稍后再试或联系技术支持。"
            error_data = None

        return ErrorResponse.internal_server_error(
            message=error_detail_message,
            data=error_data
        )