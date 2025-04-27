# models/product_model.py
"""商品模型定义（符合第三范式）"""

from peewee import AutoField, CharField, DecimalField, IntegerField
from models.base_model import BaseModel

class Product(BaseModel):
    """商品表模型"""

    id = AutoField(primary_key=True)
    name = CharField()
    price = IntegerField()
