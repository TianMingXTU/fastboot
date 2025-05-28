# fastboot/response.py
"""统一响应封装模块，使用Pydantic定义响应结构并返回JSONResponse。"""

from fastapi.responses import JSONResponse
from fastapi import status as http_status # 导入FastAPI的状态码
from typing import Any, Optional, Dict, Union, List, Generic, TypeVar
from pydantic import BaseModel, Field

# 定义一个泛型数据类型，用于响应体中的 data 字段
DataType = TypeVar('DataType')

class BaseResponseSchema(BaseModel, Generic[DataType]):
    """
    API响应的基础Pydantic模型。
    使用泛型 DataType 来支持不同类型的 'data' 字段。
    """
    success: bool = Field(..., description="操作是否成功")
    message: Optional[str] = Field(None, description="操作结果的描述信息")
    error_code: Optional[str] = Field(None, description="自定义错误码，在 success=False 时可能出现")
    data: Optional[DataType] = Field(None, description="实际的响应数据")

    class Config:
        # Pydantic V2 配置
        populate_by_name = True # 允许使用别名
        # orm_mode = True # Pydantic V1, V2 中是 from_attributes = True (如果需要从ORM对象转换)
        from_attributes = True


class SuccessResponse:
    """用于生成成功响应的辅助类。"""

    @staticmethod
    def create(
        data: Optional[DataType] = None, 
        message: str = "操作成功",
        http_code: int = http_status.HTTP_200_OK # 默认为200 OK
    ) -> JSONResponse:
        """
        创建一个标准的成功JSON响应。
        :param data: 响应数据。
        :param message: 成功消息。
        :param http_code: HTTP状态码。
        :return: FastAPI的JSONResponse对象。
        """
        response_content = BaseResponseSchema[DataType](
            success=True, 
            message=message, 
            data=data
        ).model_dump(exclude_none=True) # exclude_none=True 移除值为None的字段
        return JSONResponse(status_code=http_code, content=response_content)

    @staticmethod
    def ok(data: Optional[DataType] = None, message: str = "操作成功") -> JSONResponse:
        return SuccessResponse.create(data=data, message=message, http_code=http_status.HTTP_200_OK)

    @staticmethod
    def created(data: Optional[DataType] = None, message: str = "创建成功") -> JSONResponse:
        return SuccessResponse.create(data=data, message=message, http_code=http_status.HTTP_201_CREATED)

    @staticmethod
    def accepted(data: Optional[DataType] = None, message: str = "请求已接受处理") -> JSONResponse:
        return SuccessResponse.create(data=data, message=message, http_code=http_status.HTTP_202_ACCEPTED)
    
    @staticmethod
    def no_content(message: str = "操作成功，无内容返回") -> JSONResponse:
        # 204 No Content 通常不应包含响应体，但如果API设计需要统一格式，可以包含message
        # 如果严格遵循HTTP 204，应该返回 Response(status_code=204)
        # 此处为了统一格式，我们返回一个带消息的成功响应，但状态码仍是204
        # FastAPI 对于204会自动处理不返回body，所以这里的content可能被忽略
        response_content = BaseResponseSchema[Any](success=True, message=message).model_dump(exclude_none=True)
        return JSONResponse(status_code=http_status.HTTP_204_NO_CONTENT, content=response_content)


class ErrorResponse:
    """用于生成错误响应的辅助类。"""

    @staticmethod
    def create(
        message: str,
        error_code: Optional[str] = None,
        http_code: int = http_status.HTTP_400_BAD_REQUEST,
        data: Optional[DataType] = None # 有时错误响应也可能需要携带数据
    ) -> JSONResponse:
        """
        创建一个标准的错误JSON响应。
        :param message: 错误消息。
        :param error_code: 自定义错误码。
        :param http_code: HTTP状态码。
        :param data: (可选) 附加的错误相关数据。
        :return: FastAPI的JSONResponse对象。
        """
        response_content = BaseResponseSchema[DataType](
            success=False, 
            message=message, 
            error_code=error_code,
            data=data
        ).model_dump(exclude_none=True)
        return JSONResponse(status_code=http_code, content=response_content)

    @staticmethod
    def bad_request(message: str = "无效请求", error_code: Optional[str] = "BAD_REQUEST", data: Optional[DataType] = None) -> JSONResponse:
        return ErrorResponse.create(message=message, error_code=error_code, http_code=http_status.HTTP_400_BAD_REQUEST, data=data)

    @staticmethod
    def unauthorized(message: str = "未授权访问", error_code: Optional[str] = "UNAUTHORIZED", data: Optional[DataType] = None) -> JSONResponse:
        return ErrorResponse.create(message=message, error_code=error_code, http_code=http_status.HTTP_401_UNAUTHORIZED, data=data)

    @staticmethod
    def forbidden(message: str = "禁止访问", error_code: Optional[str] = "FORBIDDEN", data: Optional[DataType] = None) -> JSONResponse:
        return ErrorResponse.create(message=message, error_code=error_code, http_code=http_status.HTTP_403_FORBIDDEN, data=data)

    @staticmethod
    def not_found(message: str = "资源未找到", error_code: Optional[str] = "NOT_FOUND", data: Optional[DataType] = None) -> JSONResponse:
        return ErrorResponse.create(message=message, error_code=error_code, http_code=http_status.HTTP_404_NOT_FOUND, data=data)

    @staticmethod
    def unprocessable_entity(message: str = "请求数据校验失败", error_code: Optional[str] = "VALIDATION_ERROR", data: Optional[DataType] = None) -> JSONResponse:
        # 'data' 字段常用于传递详细的字段校验错误信息
        return ErrorResponse.create(message=message, error_code=error_code, http_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY, data=data)

    @staticmethod
    def internal_server_error(message: str = "服务器内部错误", error_code: Optional[str] = "INTERNAL_SERVER_ERROR", data: Optional[DataType] = None) -> JSONResponse:
        return ErrorResponse.create(message=message, error_code=error_code, http_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR, data=data)

# 使用示例:
# return SuccessResponse.ok(data={"user_id": 1, "name": "Test"})
# return ErrorResponse.not_found(message="用户ID为 123 的用户不存在。")