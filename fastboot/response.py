# fastboot/response.py
"""统一响应封装模块"""

from fastapi import HTTPException

class SuccessResponse:
    """成功响应封装"""

    @staticmethod
    def ok(data=None):
        return {
            "success": True,
            "data": data,
            "error": None
        }

class ErrorResponse:
    """错误响应封装"""

    @staticmethod
    def fail(error_message: str, status_code: int = 400):
        raise HTTPException(
            status_code=status_code,
            detail={
                "success": False,
                "data": None,
                "error": error_message
            }
        )
