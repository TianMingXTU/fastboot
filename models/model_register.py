# models/model_register.py
"""模型注册模块，统一管理需要创建的所有表。"""

from models.product_model import Product

MODELS = [
    Product,
    # 以后新加的表继续往这里加
]
