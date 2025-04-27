# models/product_model.py
"""商品模型定义（符合第三范式）"""

from peewee import AutoField, CharField, DecimalField, IntegerField
from models.base_model import BaseModel

class Product(BaseModel):
    """商品表模型"""

    id = AutoField(primary_key=True)  # 自增主键
    name = CharField(max_length=255, unique=True, null=False)  # 商品名称，唯一约束
    price = DecimalField(max_digits=10, decimal_places=2, null=False)  # 商品价格，货币型
    stock = IntegerField(default=0, null=True)  # 库存数量，默认0，允许为空
