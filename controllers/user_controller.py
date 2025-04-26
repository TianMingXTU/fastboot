# controllers/user_controller.py
"""用户控制器，提供用户注册与查询API接口。"""

from fastboot.router_scanner import controller, get, post
from services.user_service import UserService
from fastapi import HTTPException

@controller("/user")
class UserController:
    """用户相关接口控制器。"""

    def __init__(self):
        self.user_service = UserService()

    @post("/register")
    async def register(self, request: dict):
        """用户注册接口。

        Args:
            request (dict): 包含'name'和'age'的JSON请求体

        Returns:
            dict: 成功返回新用户信息
        """
        try:
            name = request.get("name")
            age = request.get("age")

            if not name or not age:
                raise HTTPException(status_code=400, detail="请求参数缺失")

            if not isinstance(age, int):
                raise HTTPException(status_code=400, detail="年龄必须是整数")

            user = self.user_service.register_user(name, age)
            return {
                "success": True,
                "data": user
            }

        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @get("/info/{user_id}")
    async def get_info(self, user_id: int):
        """用户查询接口。

        Args:
            user_id (int): 用户ID

        Returns:
            dict: 成功返回用户信息
        """
        try:
            user = self.user_service.get_user_info(user_id)
            return {
                "success": True,
                "data": user
            }
        except ValueError as ve:
            raise HTTPException(status_code=404, detail=str(ve))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
