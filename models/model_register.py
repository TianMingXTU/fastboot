# models/model_register.py
"""模型注册模块，统一管理需要创建的所有表。"""

from models.user_model import User

MODELS = [
    User,
    # 以后新加的表继续往这里加
]
