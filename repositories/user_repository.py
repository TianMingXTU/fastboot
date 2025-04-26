# repositories/user_repository.py
"""用户数据访问层，封装对User模型的数据库操作。"""

from models.user_model import User

class UserRepository:
    """用户Repository，提供标准CRUD操作接口。"""

    def get_user_by_id(self, user_id: int):
        """根据用户ID查询用户。

        Args:
            user_id (int): 用户ID

        Returns:
            dict: 用户信息字典，如果不存在返回None
        """
        try:
            user = User.get(User.id == user_id)
            return user.to_dict()
        except User.DoesNotExist:
            return None

    def create_user(self, name: str, age: int):
        """创建新用户。

        Args:
            name (str): 用户名
            age (int): 年龄

        Returns:
            dict: 新创建的用户信息
        """
        user = User.create(name=name, age=age)
        return user.to_dict()
