# models/product_model.py

"""商品模型定义（符合第三范式，Tortoise ORM版）"""

from tortoise import fields
from models.base_model import BaseModel

class Product(BaseModel):
    """商品表模型"""

    name = fields.CharField(max_length=255)
    price = fields.IntField()
