# services/user_service.py
"""用户业务逻辑层，负责处理用户注册与查询流程。"""

from repositories.user_repository import UserRepository

class UserService:
    """用户Service，处理用户相关业务逻辑。"""

    def __init__(self):
        self.user_repository = UserRepository()

    def register_user(self, name: str, age: int) -> dict:
        """注册新用户。

        Args:
            name (str): 用户名
            age (int): 年龄

        Returns:
            dict: 新用户信息

        Raises:
            ValueError: 当参数验证失败时
        """
        # 参数验证
        if not isinstance(name, str) or len(name.strip()) == 0:
            raise ValueError("用户名不能为空")
        
        if not isinstance(age, int) or age <= 0:
            raise ValueError("年龄必须是正整数")

        return self.user_repository.create_user(name, age)

    def get_user_info(self, user_id: int) -> dict:
        """根据用户ID查询用户信息。

        Args:
            user_id (int): 用户ID

        Returns:
            dict: 用户信息字典
        """
        user = self.user_repository.get_user_by_id(user_id)
        if not user:
            raise ValueError(f"用户ID {user_id} 不存在")
        return user
